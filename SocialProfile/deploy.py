from subprocess import Popen

from SocialProfile.Config import Config

if __name__ == "__main__":
    """
    Deployment's configuration is in Config/Config.py
    1. Start a virtualenv
    2. export the pythonpath in the directory where the package SocialProfile is
    3. launch this script
    """
    try:
        processes = [Popen(["../../bin/python3", 'Manager/MinerManager.py'])]

        miners = {
            "music": "TagMiners/ConcertMiner.py",
            "cinema": "TagMiners/CinemaMiner.py",
            "events": "TagMiners/EventMiner.py",
            "food": "TagMiners/FoodMiner.py"
        }

        for miner in Config.ARCHITECTURE['tag_miners']:
            for i in range(miner['miners']):
                processes.append(Popen(["../../bin/python3", miners[miner['tag']]]))

        for assembler in Config.ARCHITECTURE['vector_assemblers']:
            processes.append(Popen(["../../bin/python3", "Assembler/VectorAssembler.py", assembler["queue"]]))

        while True:
            for p in processes:
                if p.stdout:
                    print(p.stdout.read())

    except KeyboardInterrupt:
        for process in processes:
            process.kill()
