import subprocess

txt = """
德国研究人员22日报告说，
他们正开发一种新方法，
有望帮助患者从体内清除艾滋病病毒。
目前动物实验已取得成功。
"""
app = "some_app_has_stdin.sh"
with subprocess.Popen(app, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True) as proc:
    outs, errs = proc.communicate(input=txt, timeout=10)
    print(outs, errs)

# except subprocess.CalledProcessError as ex:
#     print(ex)
# else:
#     print("convert to text done: ")
