import logging
import os
import time


class Logging:

    @staticmethod
    def make_log_dir(dirname='logs'):  # 创建存放日志的目录，并返回目录的路径
        now_dir = os.path.dirname(__file__)
        father_path = os.path.dirname(now_dir)
        path = os.path.join(father_path, dirname)
        path = os.path.normpath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_log_filename(self):  # 创建日志文件的文件名格式，便于区分每天的日志
        filename = "{}.log".format(time.strftime("%Y-%m-%d",time.localtime()))
        filename = os.path.join(self.make_log_dir(),filename)
        filename = os.path.normpath(filename)
        return filename

    def log(self, level='DEBUG'):  # 生成日志的主方法,传入对那些级别及以上的日志进行处理
        logger = logging.getLogger()  # 创建日志器
        level = getattr(logging, level)  # 获取日志模块的的级别对象属性
        logger.setLevel(level)  # 设置日志级别
        if not logger.handlers:  # 作用,防止重新生成处理器
            sh = logging.StreamHandler()  # 创建控制台日志处理器
            fh = logging.FileHandler(filename=self.get_log_filename(), mode='a', encoding="utf-8")  # 创建日志文件处理器
            # 创建格式器
            fmt = logging.Formatter("%(asctime)s-%(levelname)s-%(filename)s-Line:%(lineno)d-Message:%(message)s")
            # 给处理器添加格式
            sh.setFormatter(fmt=fmt)
            fh.setFormatter(fmt=fmt)
            # 给日志器添加处理器，过滤器一般在工作中用的比较少，如果需要精确过滤，可以使用过滤器
            logger.addHandler(sh)
            logger.addHandler(fh)
        return logger  # 返回日志器


if __name__ == '__main__':
    logger = Logging().log(level='DEBUG')  # 调用封装的日志方法，生成处理后的日志器
    logger.debug("A")  # 使用日志器生成日志
    logger.info("B")
    logger.error("C")
    logger.warning("D")
    logger.critical("E")
