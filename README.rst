饭否小机器人们
==============

.. image:: https://img.shields.io/travis/akgnah/fanfou-bot/master.svg
    :target: https://travis-ci.org/akgnah/fanfou-bot

.. image:: https://img.shields.io/badge/code_style-pep8-orange.svg
    :target: https://www.python.org/dev/peps/pep-0008


环境
----

使用 Python 3.x，在 ArchLinux、Ubuntu 16.04 和 Windows 10 测试通过。

安装依赖
--------

.. code-block:: bash

   $ sudo pip install fanfou


修改配置
--------

1. 修改 conf.py 文件，把你自己的 Consumer Key、Consumer Secret、Access_Token Key 和 Access_Token Secret 填进 token 中。
   若你没有 Consumer， 可访问 `饭否应用 <https://fanfou.com/apps>`_ 页面新建一个，如何获取 Access_Token 可查看 `fanfou-py <https://github.com/akgnah/fanfou-py>`_。

2. Mr.Gretting 和 诗词君 都使用了两个账号，前者是因为早些时期饭否关注的人有上限，需要用额外的账号去关注人来获取消息；诗词君是因为配备了诗词娘来通知，当加入或退出的时候。
   你可以让 poems1 和 poems2 相同，whale1 和 whale2 相同，以此让他们都只使用一个账号。

运行
----
poems.py 是诗词君，whale.py 对应着 Mr.Gretting，下面是他们接受的参数和对应的功能：

.. code-block:: bash

   # fanfou-bot: poems
   python poems.py check     # 检查 mentions，查看是否有加入或退出
   python poems.py update    # 更新接受推送的用户的名字
   python poems.py send      # 开始推送

   # fanfou-bot: whale
   python whale.py check            # 检查 mentions 和私信
   python whale.py greet morn       # 早上工作模式
   python whale.py greet night      # 晚上工作模式
   python whale.py welcome morn     # 早上工作前打招呼
   python whale.py goodbye morn     # 早上工作结束说再见
   python whale.py welcome night    # 晚上工作前打招呼
   python whale.py goodbye night    # 晚上工作结束说再见

我使用 Crontab 来定时执行以上各选项。


致谢
----

如果你有任何疑问欢迎 Email 联系我，在我的 Github 主页能找到我的邮箱地址。感谢关注。
