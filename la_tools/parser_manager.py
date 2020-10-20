from la_tools.la_helper import *
from la_tools.la_logger import *
import pickle
import tatsu
import time
from appdirs import *
from os import listdir
from pathlib import Path
import hashlib
import importlib
import importlib.util
import threading
import shutil
from datetime import datetime
MAXIMUM_SIZE = 12  # 10 + 2 default


class ParserManager(object):
    def __init__(self):
        self.logger = LaLogger.getInstance().get_logger(LoggerTypeEnum.DEFAULT)
        self.parser_dict = {}
        self.prefix = "parser"
        self.module_dir = "iheartla"
        self.default_parsers = [hashlib.md5("init".encode()).hexdigest(), hashlib.md5("default".encode()).hexdigest()]
        # create the user's cache directory (pickle)
        self.cache_dir = os.path.join(user_cache_dir(), self.module_dir)
        dir_path = Path(self.cache_dir)
        if not dir_path.exists():
            dir_path.mkdir()
            # copy default parsers
            for f in listdir("la_local_parsers"):
                shutil.copy(os.path.join("la_local_parsers", f), self.cache_dir)
        # self.cache_file = Path(self.cache_dir + '/parsers.pickle')
        #######
        self.load_parsers()

    def load_from_pickle(self):
        # Load parsers when program launches
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    self.parser_dict = pickle.load(f)
            except Exception as e:
                print("IO error:{}".format(e))

    def load_parsers(self):
        for f in listdir(self.cache_dir):
            if self.prefix in f and '.py' in f and '_' in f:
                name = f.split('.')[0]
                hash_value = name.split('_')[1]
                module_name = "{}.{}".format(self.module_dir, name)
                path_to_file = os.path.join(self.cache_dir, "{}.py".format(name))
                spec = importlib.util.spec_from_file_location(module_name, path_to_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                parser_a = getattr(module, "grammar{}Parser".format(hash_value))
                parser_semantic = getattr(module, "grammar{}ModelBuilderSemantics".format(hash_value))
                parser = parser_a(semantics=parser_semantic())
                self.parser_dict[hash_value] = parser
        self.logger.debug("After loading, self.parser_dict:{}".format(self.parser_dict))
        if len(self.parser_dict) > 1:
            print("{} parsers loaded".format(len(self.parser_dict)))
        else:
            print("{} parser loaded".format(len(self.parser_dict)))

    def get_parser(self, key, grammar):
        hash_value = hashlib.md5(key.encode()).hexdigest()
        if hash_value in self.parser_dict:
            return self.parser_dict[hash_value]
        # os.path.dirname(filename) is used as the prefix for relative #include commands
        # It just needs to be a path inside the directory where all the grammar files are.
        parser = tatsu.compile(grammar, asmodel=True, filename=os.path.join('la_grammar', 'here'))
        self.parser_dict[hash_value] = parser
        # save to file asynchronously
        save_thread = threading.Thread(target=self.save_grammar, args=(hash_value, grammar,))
        save_thread.start()
        # self.save_dict()
        return parser

    def save_grammar(self, hash_value, grammar):
        self.check_parser_cnt()
        code = tatsu.to_python_sourcecode(grammar, name="grammar{}".format(hash_value), filename=os.path.join('la_grammar', 'here'))
        code_model = tatsu.to_python_model(grammar, name="grammar{}".format(hash_value), filename=os.path.join('la_grammar', 'here'))
        code_model = code_model.replace("from __future__ import print_function, division, absolute_import, unicode_literals", "")
        code += code_model
        save_to_file(code, os.path.join(self.cache_dir, "{}_{}_{}.py".format(self.prefix, hash_value, datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))))

    def check_parser_cnt(self):
        parser_size = len(self.parser_dict)
        self.logger.debug("check_parser_cnt, self.parser_dict:{}, max:{}".format(self.parser_dict, MAXIMUM_SIZE))
        while parser_size > MAXIMUM_SIZE:
            earliest_time = time.time()
            earliest_file = None
            earliest_hash = None
            for f in listdir(self.cache_dir):
                if self.prefix in f and '.py' in f and '_' in f:
                    name = f.split('.')[0]
                    hash_value = name.split('_')[1]
                    if hash_value not in self.default_parsers:
                        cur_time = os.path.getmtime(os.path.join(self.cache_dir, f))
                        if cur_time < earliest_time:
                            earliest_time = cur_time
                            earliest_file = f
                            earliest_hash = hash_value
            if earliest_file is not None and earliest_hash in self.parser_dict:
                del self.parser_dict[earliest_hash]
                os.remove(os.path.join(self.cache_dir, earliest_file))
                parser_size = len(self.parser_dict)
            else:
                # avoid dead loop
                break
        self.logger.debug("check_parser_cnt, self.parser_dict:{}".format(self.parser_dict))

    def save_dict(self):
        self.logger.debug("self.parser_dict:{}".format(self.parser_dict))
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.parser_dict, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            print("IO error:{}".format(e))

