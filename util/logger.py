import logging
import os
import sys
import gzip
import time
import socket
from inspect import getframeinfo, stack
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

sys.path.append("..")
from util.singleton import Singleton


class Logger(Singleton):
    def __init__(self, file_name, handler="console", debug=True):
        """
        logger 封装\n
        handler: 'file', 'time'
        """
        self.log_name = os.path.basename(file_name)

        # 创建一个logger
        self.hostname = socket.gethostname()
        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]-[thread:%(thread)s]-[process:%(process)s]%(message)s")

        # logger 开关
        if not debug:
            return

        if self.logger.hasHandlers():  # 初始化过不再初始化
            return

        # 创建一个handler，用于将日志输出到控制台 console, 默认 handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)

        if handler != "console":
            filename = os.path.realpath(__file__)
            cur_file_path = os.path.dirname(filename)
            log_path = f"{cur_file_path}/log"
            logname = f"{log_path}/{self.log_name}.log"  # 指定输出的日志文件名
            os.makedirs(log_path, exist_ok=True)
            print(f"log file path:{logname}")
            if handler == "file":
                # 写入文件，如果文件超过100M大小时，切割日志文件，仅保留3个文件
                fh = GzRotatingFileHandler(filename=logname, maxBytes=100 * 1024 * 1024, backupCount=3, encoding='utf-8')
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(self.formatter)
                self.logger.addHandler(fh)
                print(f"logger:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> add file rotation handler path:{logname}")

            if handler == "time":
                # 创建一个handler，每天生成一个文件 time
                th = GzTimedRotatingFileHandler(filename=logname, when="MIDNIGHT", backupCount=3, encoding="utf-8")
                th.suffix = "%Y-%m-%d_%H-%M-%S.log"
                th.setLevel(logging.DEBUG)
                th.setFormatter(self.formatter)
                self.logger.addHandler(th)
                print(f"logger:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> add time rotation handler path:{logname}")

    def set_handler(self, handler):
        caller = getframeinfo(stack()[1][0])
        if '/' in caller.filename:
            log_name = caller.filename.split('/')[-1]
        else:
            log_name = caller.filename.split('\\')[-1]
        """
        实例化后也可以设置handler
        handler: 'file', 'time'
        这两个 handler 只能设置一个, 否则会有冲突
        """
        filename = os.path.realpath(__file__)
        cur_file_path = os.path.dirname(filename)
        log_path = f"{cur_file_path}/log"
        logname = f"{log_path}/{log_name}.log"  # 指定输出的日志文件名
        os.makedirs(log_path, exist_ok=True)
        print(f"log file path:{logname}")
        if handler == "file":
            # 写入文件，如果文件超过100M大小时，切割日志文件，仅保留3个文件
            fh = GzRotatingFileHandler(filename=logname, maxBytes=100 * 1024 * 1024, backupCount=3, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.formatter)
            self.logger.addHandler(fh)
            print(f"logger:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> add file rotation handler path:{logname}")

        if handler == "time":
            # 创建一个handler，每天生成一个文件 time
            th = GzTimedRotatingFileHandler(filename=logname, when="MIDNIGHT", backupCount=3, encoding="utf-8")
            th.suffix = "%Y-%m-%d_%H-%M-%S.log"
            th.setLevel(logging.DEBUG)
            th.setFormatter(self.formatter)
            self.logger.addHandler(th)
            print(f"logger:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> add time rotation handler path:{logname}")

    def debug(self, msg):
        caller = getframeinfo(stack()[1][0])
        if '/' in caller.filename:
            filename = caller.filename.split('/')[-1]
        else:
            filename = caller.filename.split('\\')[-1]
        line_num = caller.lineno
        log_prefix = f"-[{filename}:{line_num}] > "

        self.logger.debug(log_prefix + str(msg))

    def info(self, msg):
        caller = getframeinfo(stack()[1][0])
        if '/' in caller.filename:
            filename = caller.filename.split('/')[-1]
        else:
            filename = caller.filename.split('\\')[-1]
        line_num = caller.lineno
        log_prefix = f"-[{filename}:{line_num}] > "

        self.logger.info(log_prefix + str(msg))

    def warning(self, msg):
        caller = getframeinfo(stack()[1][0])
        if '/' in caller.filename:
            filename = caller.filename.split('/')[-1]
        else:
            filename = caller.filename.split('\\')[-1]
        line_num = caller.lineno
        log_prefix = f"-[{filename}:{line_num}] > "

        self.logger.warning(log_prefix + str(msg))

    def error(self, msg):
        caller = getframeinfo(stack()[1][0])
        if '/' in caller.filename:
            filename = caller.filename.split('/')[-1]
        else:
            filename = caller.filename.split('\\')[-1]
        line_num = caller.lineno
        log_prefix = f"-[{filename}:{line_num}] > "

        self.logger.error(log_prefix + str(msg))


class GzRotatingFileHandler(RotatingFileHandler):

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False, errors=None):
        super().__init__(filename=filename, mode=mode, maxBytes=maxBytes, backupCount=backupCount,
                         encoding=encoding, delay=delay)

    def doGzip(self, old_log):
        with open(old_log) as old:
            with gzip.open(old_log + '.gz', 'wt') as comp_log:
                comp_log.writelines(old)
        os.remove(old_log)

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d.gz" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d.gz" % (self.baseFilename, i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            # Issue 18940: A file may not have been created if delay is True.
            if os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
                self.doGzip(dfn)
            # self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()


class GzTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None,
                 errors=None):
        super().__init__(filename=filename, when=when, interval=interval, backupCount=backupCount,
                         encoding=encoding, delay=delay, utc=utc, atTime=atTime)

    def doGzip(self, old_log):
        with open(old_log) as old:
            with gzip.open(old_log + '.gz', 'wt') as comp_log:
                comp_log.writelines(old)
        os.remove(old_log)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        # Issue 18940: A file may not have been created if delay is True.
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            self.doGzip(dfn)
        # print(f"backupCount{self.backupCount} baseFileName:{self.baseFilename}")
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        # See bpo-44753: Don't use the extension when computing the prefix.
        n, e = os.path.splitext(baseName)
        prefix = n + '.'
        plen = len(prefix)
        for fileName in fileNames:
            if self.namer is None:
                # Our files will always start with baseName
                if not fileName.startswith(baseName):
                    continue
            else:
                # Our files could be just about anything after custom naming, but
                # likely candidates are of the form
                # foo.log.DATETIME_SUFFIX or foo.DATETIME_SUFFIX.log
                if (not fileName.startswith(baseName) and fileName.endswith(e) and
                        len(fileName) > (plen + 1) and not fileName[plen + 1].isdigit()):
                    continue

            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                # See bpo-45628: The date/time suffix could be anywhere in the
                # filename
                parts = suffix.split('.')
                for part in parts:
                    if self.extMatch.match(part):
                        # print(f"result.append:{os.path.join(dirName, fileName)}")
                        result.append(os.path.join(dirName, fileName))
                        break
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


if __name__ == "__main__":
    i = 0
    logger = Logger("test_rotation")
    # logger.set_handler('file')
    logger.set_handler('time')
    while True:
        i += 1
        logger.info(f"rotation handler logger >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {i}")
        time.sleep(1)
