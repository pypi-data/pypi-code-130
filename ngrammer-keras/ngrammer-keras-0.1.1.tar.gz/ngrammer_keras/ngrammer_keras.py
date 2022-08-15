from einops import rearrange
import sympy
import tensorflow as tf
from tensorflow.keras import layers

# helper functions

def exists(val):
    return val is not None

def sum_squares(t, dim = -1):
    return tf.reduce_sum(t ** 2, dim)

# bigram related functions

def multi_way_hash_ids(x, a, b, prime, buckets):
    a = tf.cast(a, tf.int64)
    b = tf.cast(b, tf.int64)
    result = ((x * a + b) % prime) % buckets
    return result

def get_bigram_ids(ids, vocab_size):
    # ids are in shape (batch, seq, heads)
    
    batch_size = tf.shape(ids)[0]
    num_heads = tf.shape(ids)[-1]
    pad = tf.zeros([batch_size, 1, num_heads], dtype=tf.int64)  # [batch, 1]
    ids = tf.cast(ids, tf.int64)
    ids_0 = tf.concat([ids, pad], 1)  # [batch, 1+time]
    ids_1 = tf.concat([pad, ids], 1)  # [batch, 1+time]

    ngram_ids = ids_0 + ids_1 * vocab_size

    ngram_ids = ngram_ids[:, :-1]
    return ngram_ids

class VectorQuantization(layers.Layer):
    def __init__(
        self,
        *,
        num_clusters,
        num_heads,
        dim_per_head,
        decay = 0.999,
        epsilon = 1e-6
    ):
        super().__init__()
        self.decay = decay
        self.epsilon = epsilon
        self.num_heads = num_heads
        self.dim_per_head = dim_per_head
        self.num_clusters = num_clusters

        m_init = tf.random_normal_initializer()
        self.means = tf.Variable(
            initial_value=m_init(shape=(num_heads, num_clusters, dim_per_head), dtype="float32"),
            trainable=False,
        )
        
        
    def call(
        self,
        x,
        training=None,
        mask = None
    ):
        h, dim_head, num_clusters, eps, decay, means = self.num_heads, self.dim_per_head, self.num_clusters, self.epsilon, self.decay, self.means
        assert x.shape[-1] == (h * dim_head), f'input embedding feature dimension must be {h * dim_head} but shape of input is {x.shape}'

        # split heads from input

        x = rearrange(x, 'b n (h d) -> b n h d', h = h)
        print(f"Rearrange: {x.shape}")

        # get distance of input embeddings from means

        dists = (
            rearrange(sum_squares(x), 'b n h -> b n h 1')
            - 2 * tf.einsum('b n h d, h k d -> b n h k', x, means)
            + rearrange(sum_squares(means), 'h k -> 1 1 h k')
        )
        print(f"Distances from learned clusters: {dists.shape}")

        # get cluster ids

        cluster_ids = tf.math.argmin(dists, axis = -1)
        print(f"Cluster IDs for each input dimension: {cluster_ids.shape}")

        if training:
            # get one hot, for calculating number of matches per mean

            nearest_one_hot = tf.one_hot(cluster_ids, depth = num_clusters)
            per_cluster_count = tf.reduce_sum(nearest_one_hot, (0, 1))

            # sum of the input per each closest centroid.

            sum_x = tf.einsum('b n h k, b n h d -> h k d', tf.cast(nearest_one_hot, tf.float32), x)

            # calculate new means

            new_means = sum_x / (eps + rearrange(per_cluster_count, '... -> ... 1'))

            # exponential moving average

            updated_means = (1. - decay) * new_means + decay * means
            
            self.means.assign(updated_means)

        return cluster_ids

class MultiheadLayerNorm(layers.Layer):
    def __init__(self, dim, heads = 1, eps = 1e-5):
        super().__init__()
        self.eps = eps
        self.g =  tf.Variable(initial_value=tf.ones((heads, dim)), trainable=False)
        self.b =  tf.Variable(initial_value=tf.zeros((heads, dim)), trainable=False)

    def forward(self, x):
        std = tf.math.reduce_variance(x, axis = -1, unbiased = False, keepdim = True).sqrt()
        mean = tf.math.reduce_mean(x, axis = -1, keepdim = True)
        return (x - mean) / (std + self.eps) * self.g + self.b

class Ngrammer(layers.Layer):
    def __init__(
        self,
        *,
        unigram_vocab_size,
        dim_per_head,
        num_heads = 1,
        ngram_emb_dim = 8,
        ngram_vocab_size = 768 * 256,
        concat_ngrams = True
    ):
        super().__init__()
        assert not (concat_ngrams and dim_per_head <= ngram_emb_dim), 'unigram head dimension cannot be smaller than ngram embedding dimension when concatting'
        assert not (not concat_ngrams and dim_per_head == ngram_emb_dim), 'unigram head dimension must be equal to ngram embedding dimension if not concatting'

        self.num_heads = num_heads
        self.ngram_vocab_size = ngram_vocab_size
        self.unigram_vocab_size = unigram_vocab_size
        self.concat_ngrams = concat_ngrams

        self.ngram_layernorm = MultiheadLayerNorm(ngram_emb_dim, heads = num_heads)
        self.embeds_layernorm = MultiheadLayerNorm(dim_per_head, heads = num_heads)
        
        self.ngram_embeds = layers.Embedding(
            input_dim=ngram_vocab_size * num_heads, output_dim=ngram_emb_dim)

        primes = list(sympy.primerange(ngram_vocab_size + 1, 2 * ngram_vocab_size))[:num_heads]
        self.primes = tf.Variable(initial_value=primes, dtype="int64", trainable=False)

    def call(
        self,
        embeds,
        cluster_ids,
        mask = None,
        segment_pos = None
    ):
        num_heads, vocab_size, unigram_vocab_size, device = self.num_heads, self.ngram_vocab_size, self.unigram_vocab_size, embeds.device

        if len(cluster_ids.shape) == 2:
            cluster_ids = repeat(cluster_ids, '... -> ... h', h = num_heads)

        ngram_cluster_ids = get_bigram_ids(cluster_ids, unigram_vocab_size)
        print(f"ngram_cluster_ids: {ngram_cluster_ids}")

        # prepare arange of heads for parallel computation of multi-way hash ids

        head_range = tf.range(num_heads, dtype=tf.int64)
        head_range = rearrange(head_range, 'h -> 1 1 h')
        primes = rearrange(self.primes, 'h -> 1 1 h')

        # multi-way hash ids, using https://arxiv.org/abs/1504.06804

        ngram_ids = multi_way_hash_ids(ngram_cluster_ids, head_range + 1, head_range + 1, primes, vocab_size)
        print(f"ngram_ids: {ngram_ids}")

        # shift vocab range for each head appropriately by the head number

        ngram_ids = ngram_ids + (vocab_size * head_range)

        # get all n-gram embeddings in one go, and multi-head layernorm

        ngram_embeds = self.ngram_embeds(ngram_ids)
        print(self.ngram_embeds)
        normed_ngram_embeds = self.ngram_layernorm(ngram_embeds)

        # multi-head layernorm inputs

        embeds = rearrange(embeds, 'b n (h d) -> b n h d', h = num_heads)
        normed_embeds = self.embeds_layernorm(embeds)

        # concat original unigram embeds with bigram

        if self.concat_ngrams:
            input_sliced_dim = normed_embeds.shape[-1] - normed_ngram_embeds.shape[-1]

            out = tf.concat((
                normed_embeds[..., :input_sliced_dim],
                normed_ngram_embeds
            ), axis = -1)
        else:
            out = normed_embeds + normed_ngram_embeds

        # flatten

        out = rearrange(out, 'b n ... -> b n (...)')

        # mask if needed

        if exists(mask):
            out = out * rearrange(mask, 'b n -> b n 1').float()
            
        return out
    
class VQNgrammer(layers.Layer):
    def __init__(
        self,
        *,
        num_clusters,
        num_heads,
        dim_per_head,
        ngram_vocab_size = 768 * 256,
        ngram_emb_dim = 8,
        concat_ngrams = True,
        decay = 0.999,
        epsilon = 1e-6
    ):
        super().__init__()
        assert ngram_vocab_size < (num_clusters ** 2), 'the ngram vocab size should be less than the number of clusters squared'

        self.vq = VectorQuantization(
            num_clusters = num_clusters,
            num_heads = num_heads,
            dim_per_head = dim_per_head,
            decay = decay,
            epsilon = epsilon
        )

        self.ngram = Ngrammer(
            unigram_vocab_size = num_clusters,
            ngram_vocab_size = ngram_vocab_size,
            ngram_emb_dim = ngram_emb_dim,
            concat_ngrams = concat_ngrams,
            num_heads = num_heads,
            dim_per_head = dim_per_head
        )

    def call(
        self,
        x,
        mask = None,
        segment_pos = None
    ):

        cluster_ids = self.vq(x, mask = mask)
        out = self.ngram(
            x,
            cluster_ids = cluster_ids,
            mask = mask,
            segment_pos = segment_pos
        )

        return out