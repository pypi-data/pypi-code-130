from datetime import datetime


import rayleaf
from rayleaf.entities import Server, Client


def fedavg_cnn(
    dataset: str,
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
    use_grads = False,
    notes: str = None
):
    curr_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    if use_grads:
        def make_fedavg_server_client():
            class FedAvgClient(Client):
                def train(self, server_update):
                    self.model_params = server_update
                    grads = self.train_model(compute_grads=True)

                    return {
                        "grads": grads,
                        "samples": self.num_train_samples
                    }
            

            class FedAvgServer(Server):
                def update_model(self, client_updates):
                    num_samples = 0
                    average_grads = 0

                    for update in client_updates:
                        average_grads += update["grads"] * update["samples"]
                        num_samples += update["samples"]
                    
                    average_grads /= num_samples

                    return self.model_params + average_grads
            

            return FedAvgServer, FedAvgClient

        
        FedAvgServer, FedAvgClient = make_fedavg_server_client()
    else:
        FedAvgServer, FedAvgClient = Server, Client

    if dataset == "femnist":
        model = "cnn"
    elif dataset == "speech_commands":
        model = "m5"

    rayleaf.run_experiment(
        dataset = dataset,
        dataset_dir = f"../data/{dataset}/",
        output_dir= f"output/fedavg-{dataset}-{curr_time}/",
        model = model,
        num_rounds = num_rounds,
        eval_every = eval_every,
        ServerType=FedAvgServer,
        client_types=[(FedAvgClient, num_clients)],
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
