# This file is MACHINE GENERATED! Do not edit.
# Generated by: tensorflow/python/tools/api/generator/create_python_api.py script.
"""Support for training models.

See the [Training](https://tensorflow.org/api_guides/python/train) guide.

"""

import sys as _sys

from . import experimental
from . import queue_runner
from tensorflow.python.checkpoint.checkpoint import CheckpointV1 as Checkpoint
from tensorflow.python.checkpoint.checkpoint_management import CheckpointManager
from tensorflow.python.checkpoint.checkpoint_management import checkpoint_exists
from tensorflow.python.checkpoint.checkpoint_management import generate_checkpoint_state_proto
from tensorflow.python.checkpoint.checkpoint_management import get_checkpoint_mtimes
from tensorflow.python.checkpoint.checkpoint_management import get_checkpoint_state
from tensorflow.python.checkpoint.checkpoint_management import latest_checkpoint
from tensorflow.python.checkpoint.checkpoint_management import remove_checkpoint
from tensorflow.python.checkpoint.checkpoint_management import update_checkpoint_state
from tensorflow.python.checkpoint.checkpoint_options import CheckpointOptions
from tensorflow.python.eager.remote import ServerDef
from tensorflow.python.framework.graph_io import write_graph
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import cosine_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import cosine_decay_restarts
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import exponential_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import inverse_time_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import linear_cosine_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import natural_exp_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import noisy_linear_cosine_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import piecewise_constant
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import piecewise_constant as piecewise_constant_decay
from tensorflow.python.keras.optimizer_v2.legacy_learning_rate_decay import polynomial_decay
from tensorflow.python.ops.gen_sdca_ops import sdca_fprint
from tensorflow.python.ops.gen_sdca_ops import sdca_optimizer
from tensorflow.python.ops.gen_sdca_ops import sdca_shrink_l1
from tensorflow.python.summary.summary_iterator import summary_iterator
from tensorflow.python.training.adadelta import AdadeltaOptimizer
from tensorflow.python.training.adagrad import AdagradOptimizer
from tensorflow.python.training.adagrad_da import AdagradDAOptimizer
from tensorflow.python.training.adam import AdamOptimizer
from tensorflow.python.training.basic_loops import basic_train_loop
from tensorflow.python.training.basic_session_run_hooks import CheckpointSaverHook
from tensorflow.python.training.basic_session_run_hooks import CheckpointSaverListener
from tensorflow.python.training.basic_session_run_hooks import FeedFnHook
from tensorflow.python.training.basic_session_run_hooks import FinalOpsHook
from tensorflow.python.training.basic_session_run_hooks import GlobalStepWaiterHook
from tensorflow.python.training.basic_session_run_hooks import LoggingTensorHook
from tensorflow.python.training.basic_session_run_hooks import NanLossDuringTrainingError
from tensorflow.python.training.basic_session_run_hooks import NanTensorHook
from tensorflow.python.training.basic_session_run_hooks import ProfilerHook
from tensorflow.python.training.basic_session_run_hooks import SecondOrStepTimer
from tensorflow.python.training.basic_session_run_hooks import StepCounterHook
from tensorflow.python.training.basic_session_run_hooks import StopAtStepHook
from tensorflow.python.training.basic_session_run_hooks import SummarySaverHook
from tensorflow.python.training.checkpoint_utils import checkpoints_iterator
from tensorflow.python.training.checkpoint_utils import init_from_checkpoint
from tensorflow.python.training.checkpoint_utils import list_variables
from tensorflow.python.training.checkpoint_utils import load_checkpoint
from tensorflow.python.training.checkpoint_utils import load_variable
from tensorflow.python.training.coordinator import Coordinator
from tensorflow.python.training.coordinator import LooperThread
from tensorflow.python.training.device_setter import replica_device_setter
from tensorflow.python.training.ftrl import FtrlOptimizer
from tensorflow.python.training.gradient_descent import GradientDescentOptimizer
from tensorflow.python.training.input import batch
from tensorflow.python.training.input import batch_join
from tensorflow.python.training.input import input_producer
from tensorflow.python.training.input import limit_epochs
from tensorflow.python.training.input import match_filenames_once
from tensorflow.python.training.input import maybe_batch
from tensorflow.python.training.input import maybe_batch_join
from tensorflow.python.training.input import maybe_shuffle_batch
from tensorflow.python.training.input import maybe_shuffle_batch_join
from tensorflow.python.training.input import range_input_producer
from tensorflow.python.training.input import shuffle_batch
from tensorflow.python.training.input import shuffle_batch_join
from tensorflow.python.training.input import slice_input_producer
from tensorflow.python.training.input import string_input_producer
from tensorflow.python.training.momentum import MomentumOptimizer
from tensorflow.python.training.monitored_session import ChiefSessionCreator
from tensorflow.python.training.monitored_session import MonitoredSession
from tensorflow.python.training.monitored_session import MonitoredTrainingSession
from tensorflow.python.training.monitored_session import Scaffold
from tensorflow.python.training.monitored_session import SessionCreator
from tensorflow.python.training.monitored_session import SingularMonitoredSession
from tensorflow.python.training.monitored_session import WorkerSessionCreator
from tensorflow.python.training.moving_averages import ExponentialMovingAverage
from tensorflow.python.training.optimizer import Optimizer
from tensorflow.python.training.proximal_adagrad import ProximalAdagradOptimizer
from tensorflow.python.training.proximal_gradient_descent import ProximalGradientDescentOptimizer
from tensorflow.python.training.py_checkpoint_reader import NewCheckpointReader
from tensorflow.python.training.quantize_training import do_quantize_training_on_graphdef
from tensorflow.python.training.queue_runner_impl import QueueRunner
from tensorflow.python.training.queue_runner_impl import add_queue_runner
from tensorflow.python.training.queue_runner_impl import start_queue_runners
from tensorflow.python.training.rmsprop import RMSPropOptimizer
from tensorflow.python.training.saver import Saver
from tensorflow.python.training.saver import export_meta_graph
from tensorflow.python.training.saver import import_meta_graph
from tensorflow.python.training.server_lib import ClusterSpec
from tensorflow.python.training.server_lib import Server
from tensorflow.python.training.session_manager import SessionManager
from tensorflow.python.training.session_run_hook import SessionRunArgs
from tensorflow.python.training.session_run_hook import SessionRunContext
from tensorflow.python.training.session_run_hook import SessionRunHook
from tensorflow.python.training.session_run_hook import SessionRunValues
from tensorflow.python.training.supervisor import Supervisor
from tensorflow.python.training.sync_replicas_optimizer import SyncReplicasOptimizer
from tensorflow.python.training.training import BytesList
from tensorflow.python.training.training import ClusterDef
from tensorflow.python.training.training import Example
from tensorflow.python.training.training import Feature
from tensorflow.python.training.training import FeatureList
from tensorflow.python.training.training import FeatureLists
from tensorflow.python.training.training import Features
from tensorflow.python.training.training import FloatList
from tensorflow.python.training.training import Int64List
from tensorflow.python.training.training import JobDef
from tensorflow.python.training.training import SaverDef
from tensorflow.python.training.training import SequenceExample
from tensorflow.python.training.training_util import assert_global_step
from tensorflow.python.training.training_util import create_global_step
from tensorflow.python.training.training_util import get_global_step
from tensorflow.python.training.training_util import get_or_create_global_step
from tensorflow.python.training.training_util import global_step
from tensorflow.python.training.warm_starting_util import VocabInfo
from tensorflow.python.training.warm_starting_util import warm_start