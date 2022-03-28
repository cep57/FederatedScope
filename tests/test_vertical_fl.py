# Copyright (c) Alibaba, Inc. and its affiliates.
import unittest

from federatedscope.core.auxiliaries.data_builder import get_data
from federatedscope.core.auxiliaries.worker_builder import get_client_cls, get_server_cls
from federatedscope.core.auxiliaries.utils import setup_seed, setup_logger
from federatedscope.config import cfg
from federatedscope.core.DAIL_fed_api import DAILFed


class vFLTest(unittest.TestCase):
    def setUp(self):
        print(('Testing %s.%s' % (type(self).__name__, self._testMethodName)))

    def set_config(self, cfg):
        backup_cfg = cfg.clone()

        cfg.use_gpu = False

        cfg.federate.mode = 'standalone'
        cfg.federate.total_round_num = 30
        cfg.federate.client_num = 2

        cfg.model.type = 'lr'
        cfg.model.use_bias = False

        cfg.optimizer.lr = 0.05

        cfg.data.type = 'vertical_fl_data'
        cfg.data.size = 50

        cfg.vertical.use = True
        cfg.vertical.key_size = 256

        cfg.trainer.type = 'none'
        cfg.eval.freq = 5

        return backup_cfg

    def test_vFL(self):
        backup_cfg = self.set_config(cfg)
        setup_seed(cfg.seed)
        setup_logger(cfg)

        data, modified_config = get_data(cfg.clone())
        cfg.merge_from_other_cfg(modified_config)
        self.assertIsNotNone(data)

        Fed_runner = DAILFed(data=data,
                             server_class=get_server_cls(cfg),
                             client_class=get_client_cls(cfg),
                             config=cfg.clone())
        self.assertIsNotNone(Fed_runner)
        test_results = Fed_runner.run()
        cfg.merge_from_other_cfg(backup_cfg)
        self.assertGreater(test_results['server_global_eval']['acc'], 0.9)


if __name__ == '__main__':
    unittest.main()