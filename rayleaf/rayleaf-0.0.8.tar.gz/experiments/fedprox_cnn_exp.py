import torch

from torch import Tensor


import rayleaf
from rayleaf.entities import Server, Client


def fedprox_cnn(
    mu: float,
    output_dir: str,
    num_rounds: int = 100,
    eval_every: int = 10,
    num_clients: int = 200,
    clients_per_round: int = 40,
    client_lr: float = 0.05,
    batch_size: int = 64,
    seed: int = 0,
    num_epochs: int = 10,
    gpus_per_client_cluster: float = 1,
    num_client_clusters: int = 8,
    save_model: bool = False,
    notes: str = None
):
    class FedProxClient(Client):
        def compute_loss(self, probs: Tensor, targets: Tensor) -> Tensor:
            loss = self.model.loss_fn(probs, targets)

            for w, wt in zip(self.model_params, self.server_model_params):
                loss += (mu / 2) * torch.pow(torch.linalg.norm(w - wt), 2)
            
            return loss

    rayleaf.run_experiment(
        dataset = "femnist",
        dataset_dir = "../data/femnist/",
        output_dir = output_dir,
        model = "cnn",
        num_rounds = num_rounds,
        eval_every = eval_every,
        ServerType=Server,
        client_types=[(FedProxClient, num_clients)],
        clients_per_round = clients_per_round,
        client_lr = client_lr,
        batch_size = batch_size,
        seed = seed,
        use_val_set = False,
        num_epochs = num_epochs,
        gpus_per_client_cluster = gpus_per_client_cluster,
        num_client_clusters = num_client_clusters,
        save_model = save_model,
        notes = notes
    )
