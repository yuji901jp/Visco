from actions import exec_cmd
from actions import startup
import time

def getprocess(monitorprocess):
    ps      = ['ps']
    option  = ['-C']
    process = [monitorprocess]
    cmd = ps+option+process
    stdout, stderr = exec_cmd.oscmd(cmd, shell=False)

    return stdout, stderr

if __name__ == '__main__':

    while True:
        stdout, stderr = getprocess('julius')
        stamp = exec_cmd.timestamp()

        if len(stdout.strip().split('\n')) < 2:
            print('[DEBUG]---- : stdout is :', stdout.strip().split('\n'), end='')
            print(stamp, ': juliusがサボってます。juliusの起動スクリプトを実行します。')
            
            # 設定ファイルの読みこみ
            jfile = 'setting.json'
            jsondata = startup.readjson(jfile)

            # 基本設定とjuliusの起動
            startup.setenv(jsondata)
            p = startup.startjulius(jsondata)

        else:
            print('[DEBUG]---- : stdout is :', stdout.strip().split('\n'), end='')
            print(stamp, ': juliusは頑張っているようです。')

        time.sleep(5)


    print('[DEBUG]---- : stdout is :', stdout.strip().split('\n'))
    print('[DEBUG]---- : stderr is :', stderr)
