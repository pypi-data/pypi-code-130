'''
This module implements the Cross Entropy Method (CEM) for sampling of low quantiles.

The user should have a stochastic process P(score; theta), whose distribution
depends on the parameter theta (the module was originally developed to sample
"difficult" conditions in reinforcement learning, so theta was the parameters
of the environment, and the score was the return of the episode).

The basic CEM class is abstract: any use of it requires inheritance with
implementation of the following methods:
- do_sample(dist): returning a sample from the distribution represented by dist.
- pdf(x, dist): the probability of x under the distribution dist.
- update_sample_distribution(samples, weights): updating dist given new samples.
- likelihood_ratio(x) (optional): implemented by default as
                                  pdf(x, orig_dist) / pdf(x, curr_dist).
                                  the user may provide a more efficient or stable
                                  implementation according to the underlying
                                  family of distributions.
Note that dist is an object that represents the distribution, and its type is
up to the user. A standard type may be a list of distribution parameters.

Examples for inheritance from CEM (CEM_Ber, CEM_Beta) are provided in examples.py,
as well as a simple usage example (__main__).

Module structure:
CEM:
    sample(): return a sample from the current distribution, along with a weight
              corresponding to the likelihood-ratio wrt the original distribution.
        do_sample(curr_dist): do the sampling.              [IMPLEMENTED BY USER]
        get_weight(x): calculate the LR weight.
            likelihood_ratio(x).
                pdf(x, dist).                               [IMPLEMENTED BY USER]
    update(score):
        update list of scores.
        if there're enough samples and it's time to update the distribution:
            select_samples().
            update_sample_distribution(samples, weights).   [IMPLEMENTED BY USER]

Written by Ido Greenberg, 2022.
'''

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle as pkl
import copy, warnings


class CEM:
    def __init__(self, phi0, batch_size=0, ref_mode='train', ref_q=None, ref_alpha=0.05,
                 n_orig_per_batch=None, min_batch_update=0.2, force_min_samples=True,
                 w_clip=0, title='CEM'):
        self.title = title
        self.default_dist_titles = None
        self.default_samp_titles = None

        # An object defining the original distribution to sample from.
        # This can be any object (e.g., list of distribution parameters),
        # depending on the implementation of the inherited class.
        self.original_dist = phi0

        # Number of samples to draw before updating distribution.
        # 0 is interpreted as infinity.
        self.batch_size = batch_size

        # Clip the likelihood-ratio weights to the range [1/w_clip, w_clip].
        # If None or 0 - no clipping is done.
        self.w_clip = w_clip

        # How to use reference scores to determine the threshold for the
        # samples selected for distribution update?
        # If req_q is not None, then ref_q is the constant value of the threshold.
        # Otherwise, it is determined by ref_mode:
        # - 'none': ignore reference scores.
        # - 'train': every batch, draw the first n=n_orig_per_batch samples
        #            from the original distribution instead of the updated one.
        #            then use quantile(batch_scores[:n]; ref_alpha).
        # - 'valid': use quantile(external_validation_scores; ref_alpha).
        #            in this case, update_ref_scores() must be called to
        #            feed reference scores before updating the distribution.
        # In CVaR optimization, ref_alpha would typically correspond to
        # the CVaR risk level.
        self.ref_q = ref_q
        self.ref_mode = ref_mode
        self.ref_alpha = ref_alpha

        # Number of samples to draw every batch from the original distribution
        # instead of the updated one. Either integer or ratio in (0,1).
        if n_orig_per_batch is None:
            n_orig_per_batch = 0.2 if self.ref_q is None and self.ref_mode!='none' else 0
        self.n_orig_per_batch = n_orig_per_batch
        if 0<self.n_orig_per_batch<1:
            self.n_orig_per_batch = int(self.n_orig_per_batch*self.batch_size)
        if self.batch_size < self.n_orig_per_batch:
            warnings.warn(f'samples per batch = {self.batch_size} < '
                          f'{self.n_orig_per_batch} = original-dist samples per batch')
            self.n_orig_per_batch = self.batch_size

        active_train_mode = self.ref_mode == 'train' and self.batch_size and self.ref_q is None
        if active_train_mode and self.n_orig_per_batch < 1:
            raise ValueError('"train" reference mode must come with a positive'
                             'number of original-distribution samples per batch.')

        # In a distribution update, use from the current batch at least
        # min_batch_update * (batch_size - n_orig_per_batch)
        # samples. min_batch_update should be in the range (0,1).
        self.min_batch_update = min_batch_update
        if active_train_mode:
            self.min_batch_update *= 1 - self.n_orig_per_batch / self.batch_size
        # If multiple scores R equal the alpha quantile q, then the selected
        #  R<q samples may be strictly fewer than min_batch_update*batch_size.
        #  If force_min_samples==True, we fill in the missing entries from
        #  samples with R==q.
        self.force_min_samples = force_min_samples

        # State
        self.batch_count = 0
        self.sample_count = 0
        self.update_count = 0
        self.ref_scores = None

        # Data
        self.sample_dist = []  # n_batches
        self.sampled_data = [[]]  # n_batches x batch_size
        self.weights = [[]]  # n_batches x batch_size
        self.scores = [[]]  # n_batches x batch_size
        self.ref_quantile = []  # n_batches
        self.internal_quantile = []  # n_batches
        self.selected_samples = [[]]  # n_batches x batch_size
        self.n_update_samples = []  # n_batches

        self.reset()

    def reset(self):
        self.batch_count = 0
        self.sample_count = 0
        self.update_count = 0
        self.ref_scores = None

        self.sample_dist = [copy.copy(self.original_dist)]
        self.sampled_data = [[]]
        self.weights = [[]]
        self.scores = [[]]
        self.ref_quantile = []
        self.internal_quantile = []
        self.selected_samples = [[]]
        self.n_update_samples = []

    def save(self, filename=None, base_path='./models', create_dir=True):
        if not os.path.exists(base_path) and create_dir:
            warnings.warn(f'Creating directory "{base_path}".')
            os.makedirs(base_path)
        if filename is None: filename = f'{base_path}/{self.title}'
        filename += '.cem'
        obj = (
            self.title, self.original_dist, self.batch_size, self.w_clip, self.ref_q,
            self.ref_mode, self.ref_alpha, self.n_orig_per_batch, self.min_batch_update,
            self.batch_count, self.sample_count, self.update_count, self.ref_scores,
            self.sample_dist, self.sampled_data, self.weights, self.scores,
            self.ref_quantile, self.internal_quantile, self.selected_samples,
            self.n_update_samples
        )
        with open(filename, 'wb') as h:
            pkl.dump(obj, h)

    def load(self, filename=None, base_path='./models'):
        if filename is None: filename = f'{base_path}/{self.title}'
        filename += '.cem'
        with open(filename, 'rb') as h:
            obj = pkl.load(h)
        self.title, self.original_dist, self.batch_size, self.w_clip, self.ref_q, \
        self.ref_mode, self.ref_alpha, self.n_orig_per_batch, self.min_batch_update, \
        self.batch_count, self.sample_count, self.update_count, self.ref_scores, \
        self.sample_dist, self.sampled_data, self.weights, self.scores, \
        self.ref_quantile, self.internal_quantile, self.selected_samples, \
        self.n_update_samples = obj

    def is_original_dist(self):
        return self.sample_count < self.n_orig_per_batch

    ########   Sampling-related methods   ########

    def sample(self):
        orig_dist = self.is_original_dist()
        dist = self.sample_dist[0] if orig_dist else self.sample_dist[-1]
        x = self.do_sample(dist)
        w = self.get_weight(x, orig_dist)
        self.sampled_data[-1].append(x)
        self.weights[-1].append(w)
        self.sample_count += 1
        if 0 < self.batch_size < self.sample_count:
            warnings.warn(f'Drawn {self.sample_count}>{self.batch_size} samples '
                          f'without updating (only {self.update_count}<'
                          f'{self.batch_size} scores for update)')
        return x, w

    def get_weight(self, x, use_original_dist=False):
        if use_original_dist:
            return 1

        lr = self.likelihood_ratio(x)
        if self.w_clip:
            lr = np.clip(lr, 1/self.w_clip, self.w_clip)
        return lr

    def likelihood_ratio(self, x, use_original_dist=False):
        if use_original_dist:
            return 1
        return self.pdf(x, self.sample_dist[0]) / \
               self.pdf(x, self.sample_dist[-1])

    def do_sample(self, dist):
        '''Given dist. parameters, return a sample drawn from the distribution.'''
        raise NotImplementedError()

    def pdf(self, x, dist):
        '''Given a sample x and distribution parameters dist, return P(x|dist).'''
        raise NotImplementedError()

    ########   Update-related methods   ########

    def update(self, score, save=True):
        self.scores[-1].append(score)
        self.update_count += 1

        if 0 < self.batch_size <= self.update_count:

            self.select_samples()
            samples = [self.sampled_data[-1][i] for i in range(self.sample_count)
                       if self.selected_samples[-1][i]]
            weights = [self.weights[-1][i] for i in range(self.sample_count)
                       if self.selected_samples[-1][i]]

            if len(samples) > 0:
                dist = self.update_sample_distribution(samples, weights)
            else:
                dist = self.sample_dist[-1]
            self.sample_dist.append(dist)

            self.reset_batch()
            if save:
                filename = save if isinstance(save, str) else None
                self.save(filename)

    def reset_batch(self):
        self.sampled_data.append([])
        self.scores.append([])
        self.weights.append([])
        self.batch_count += 1
        self.sample_count = 0
        self.update_count = 0

    def select_samples(self):
        # Get internal quantile
        q_int = quantile(self.scores[-1], self.min_batch_update)

        # Get reference quantile from "external" data
        q_ref = -np.inf
        if self.ref_q is not None:
            q_ref = self.ref_q
        elif self.ref_mode == 'train':
            q_ref = quantile(self.scores[-1][:self.n_orig_per_batch],
                             self.ref_alpha, estimate_underlying_quantile=True)
        elif self.ref_mode == 'valid':
            if self.ref_scores is None:
                warnings.warn('ref_mode=valid, but no '
                              'validation scores were provided.')
            else:
                q_ref = quantile(self.ref_scores, 100*self.ref_alpha,
                                 estimate_underlying_quantile=True)
        elif self.ref_mode == 'none':
            q_ref = -np.inf
        else:
            warnings.warn(f'Invalid ref_mode: {self.ref_mode}')

        # Take the max over the two
        self.internal_quantile.append(q_int)
        self.ref_quantile.append(q_ref)
        q = max(q_int, q_ref)

        # Select samples
        R = np.array(self.scores[-1])
        selection = R < q
        if self.force_min_samples:
            missing_samples = int(
                self.min_batch_update*self.batch_size - np.sum(selection))
            if missing_samples > 0:
                samples_to_add = np.where(R == q)[0]
                if missing_samples < len(samples_to_add):
                    samples_to_add = np.random.choice(
                        samples_to_add, missing_samples, replace=False)
                selection[samples_to_add] = True
        self.selected_samples.append(selection)
        self.n_update_samples.append(int(np.sum(selection)))

    def update_ref_scores(self, scores):
        self.ref_scores = scores

    def update_sample_distribution(self, samples, weights):
        '''Return the parameters of a distribution given samples.'''
        raise NotImplementedError()

    ########   Analysis-related methods   ########

    def get_data(self, dist_obj_titles=None, sample_dimension_titles=None,
                 exclude_last_batch=True):
        if dist_obj_titles is None:
            dist_obj_titles = self.default_dist_titles
        if sample_dimension_titles is None:
            sample_dimension_titles = self.default_samp_titles
        n_batches = self.batch_count + 1 - bool(exclude_last_batch)
        bs = self.batch_size
        if bs == 0: bs = self.sample_count

        # Batch-level data
        # Create a map from table-titles to distribution parameters.
        sd = self.sample_dist[:-1] if exclude_last_batch else self.sample_dist
        dist_objs = {}
        if isinstance(dist_obj_titles, str):
            dist_objs = {dist_obj_titles:sd}
        elif isinstance(dist_obj_titles, (tuple, list)):
            dist_objs = {t:[ds[i] for ds in sd]
                         for i,t in enumerate(dist_obj_titles)}

        d1_dict = dict(
            title=self.title,
            batch=np.arange(n_batches),
            ref_quantile=self.ref_quantile,
            internal_quantile=self.internal_quantile,
            n_update_samples=self.n_update_samples,
            update_samples_perc=100*np.array(self.n_update_samples)/bs,
        )
        for k,v in dist_objs.items():
            d1_dict[k] = v
        d1 = pd.DataFrame(d1_dict)

        # Sample-level data
        # Create a map from table-titles to sampled dimensions.
        samples = {}
        if isinstance(sample_dimension_titles, str):
            samples = {sample_dimension_titles:np.concatenate(self.sampled_data)}
        elif isinstance(sample_dimension_titles, (tuple, list)):
            sampled_data = self.sampled_data[:-1] if exclude_last_batch \
                else self.sampled_data
            samples = {t:[sample[i] for batch in sampled_data
                          for sample in batch]
                         for i,t in enumerate(sample_dimension_titles)}

        w, s = self.weights, self.scores
        if n_batches and exclude_last_batch:
            w, s = self.weights[:-1], self.scores[:-1]
        d2_dict = dict(
            title=self.title,
            batch=np.repeat(np.arange(n_batches), bs),
            sample_id=n_batches*list(range(bs)),
            selected=np.concatenate(self.selected_samples),
            weight=np.concatenate(w),
            score=np.concatenate(s),
        )
        for k,v in samples.items():
            d2_dict[k] = v
        d2 = pd.DataFrame(d2_dict)

        return d1, d2

    def show_sampled_scores(self, ax=None, ylab=None):
        if ax is None:
            ax = plt.subplots(1, 1, figsize=(5,3.5))[1]
            ax.grid(color='k', linestyle=':', linewidth=0.3)
        if ylab is None:
            ylab = 'score'

        if self.ref_q is not None:
            cvar = lambda x, alpha: np.mean(x[x <= self.ref_q])
            cvar_lab = f'mean$\\{{x|x <= {self.ref_q}\\}}$'
        elif self.ref_mode=='none':
            cvar = None
        else:
            cvar = lambda x, alpha: np.mean(np.sort(x)[:int(np.ceil(alpha*len(x)))])
            cvar_lab = f'CVaR$_{{{100*self.ref_alpha:.0f}\%}}$'

        c1, c2 = self.get_data()
        c2['orig'] = c2.sample_id < self.n_orig_per_batch
        if self.n_orig_per_batch > 0:
            mean_orig = c2[c2.orig].groupby('batch').apply(lambda d: d.score.mean())
            ax.plot(mean_orig, label='Reference mean')
            if cvar is not None:
                cvar_orig = c2[c2.orig].groupby('batch').apply(
                    lambda d: cvar(d.score.values,self.ref_alpha))
                ax.plot(cvar_orig, label=f'Reference {cvar_lab:s}')

        mean_samp = c2[~c2.orig].groupby('batch').apply(lambda d: d.score.mean())
        ax.plot(mean_samp, label='Sample mean')
        if cvar is not None:
            cvar_samp = c2[~c2.orig].groupby('batch').apply(
                lambda d: cvar(d.score.values,self.ref_alpha))
            ax.plot(cvar_samp, label=f'Sample {cvar_lab:s}')

        ax.set_xlabel('iteration', fontsize=15)
        ax.set_ylabel(ylab, fontsize=15)
        ax.legend(fontsize=14)
        return ax


def quantile(x, q, w=None, is_sorted=False, estimate_underlying_quantile=False):
    n = len(x)
    # If we estimate_underlying_quantile, we refer to min(x),max(x) not as
    #  quantiles 0,1, but rather as quantiles 1/(n+1),n/(n+1) of the
    #  underlying distribution from which x is sampled.
    if estimate_underlying_quantile and n > 1:
        q = q * (n+1)/(n-1) - 1/(n-1)
        q = np.clip(q, 0, 1)
    # Unweighted quantiles
    if w is None:
        return np.percentile(x, 100*q)
    # Weighted quantiles
    x = np.array(x)
    w = np.array(w)
    if not is_sorted:
        ids = np.argsort(x)
        x = x[ids]
        w = w[ids]
    w = np.cumsum(w) - 0.5*w
    w -= w[0]
    w /= w[-1]
    return np.interp(q, w, x)
