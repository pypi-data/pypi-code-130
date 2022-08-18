import json
import os
import pathlib
from typing import Any, Dict

import numpy as np
import tensorflow as tf
import tqdm

import kolibri
from kolibri.data.text.generators import DataGenerator, Seq2SeqDataSet
from kolibri.backend.tensorflow.autoencoder.decoders.lstm_decoder import Decoder
from kolibri.backend.tensorflow.autoencoder.encoders.lstm_encoder import Encoder
from kolibri.backend.tensorflow.utils import get_loss_object
from kolibri.logger import get_logger

logger = get_logger(__name__)

EVALUATION_INTERVAL=150

class BaseAutoEncoder:
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tf_version': tf.__version__,  # type: ignore
            'kolibri_version': kolibri.__version__,
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': {
                "configs":self.configs,
                'input_shape': self.input_shape,
                'output_shape': self.output_shape
            },

            'encoder': self.encoder.to_dict(),  # type: ignore
            'decoder': self.decoder.to_dict(),

        }

    def __init__(self, configs, input_shape, output_shape):
        super(BaseAutoEncoder, self).__init__()
        self.ae_model = None
        self.configs=configs
        self.model_name= configs["model-name"]
        self.model_chekpoint_path = os.path.join(configs["output-folder"], 'Checkpoints', self.model_name)
        self.input_shape=input_shape
        self.output_shape=output_shape
        self.title = "AutoEncoder training History"
        self.encoder = Encoder(self.input_shape, dropout=configs["dropout"])
        self.decoder = Decoder(self.output_shape, self.encoder.encoder_states, dropout=configs["dropout"])
        self.loss=configs["ae-loss"]
        # encoder decoder model
        self.ae_model = tf.keras.Model([self.encoder.encoder_input, self.decoder.decoder_input], self.decoder.decoder_output)
        self.ae_model.compile(loss=self.loss, optimizer='adam')
        self.history=None
        self.title=""

    def summary(self):
        if self.ae_model is not None:
            return self.ae_model.summary()

    def fit(self, encoder_train, decoder_train, label_train, encoder_val=None, decoder_val=None, label_val=None,
                epochs=500, patience=10):
            if self.ae_model is None:
                return

            self.history = self.ae_model.fit(
                [encoder_train, decoder_train],
                label_train, epochs=epochs, steps_per_epoch=EVALUATION_INTERVAL, validation_data=([encoder_val,
                                                                                                   decoder_val],
                                                                                                  label_val), verbose=1,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=patience, verbose=1,
                                                     mode='min'),
                    tf.keras.callbacks.ModelCheckpoint(self.model_chekpoint_path, monitor='val_loss', save_best_only=True,
                                                       mode='min',
                                                       verbose=0)])


    def save(self, model_path: str) -> str:
        """
        Save model
        Args:
            model_path:
        """

        pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
        model_path_full = os.path.abspath(model_path)

        with open(os.path.join(model_path_full, 'model_config.json'), 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
            f.close()

        self.ae_model.save_weights(os.path.join(model_path_full, self.model_name))

        logger.info('model saved to {}'.format(os.path.abspath(model_path_full)))

        if self.configs["remote-storage"]=="azure-blob":
            self.to_azure_blob(model_path_full)

        return model_path



    def to_azure_blob(self, model_path):
        """
        Save model
        Args:
            model_path:
        """


        from azure.storage.blob import BlobServiceClient

        connect_str=os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        # # Create a unique name for the container
        container_name = self.configs["container-name"]
        local_config_file = os.path.join(model_path, 'model_config.json')
        blob_local_config_file=self.__class__.__name__+'.model_config.json'
        blob_local_weight_file=self.__class__.__name__+'.model_weights.h5'

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_local_config_file)
        if not blob_client:
            container_client = blob_service_client.create_container(container_name)
            # Create a blob client using the local file name as the name for the blob
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_local_config_file)

        print("\nUploading to Azure Storage as blob")

        # Upload the created file
        with open(local_config_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_local_weight_file)

        local_model_file=os.path.join(model_path, self.model_name)

        # Upload the created file
        with open(local_model_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return container_name

    @classmethod
    def load_model(cls, model_path):
        from kolibri.backend.tensorflow.utils import load_data_object
        model_config_path = os.path.join(model_path, 'model_config.json')
        model_config = json.loads(open(model_config_path, 'r').read())
        model = load_data_object(model_config)

        model.ae_model.load_weights(os.path.join(model_path, model.model_name))
        model.encoder.built = True

        return model


    def predict(self, encoder_data, decoder_data):
        return self.ae_model.predict([encoder_data, decoder_data])



