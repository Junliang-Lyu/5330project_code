def read_db_config(filename='db_config.txt'):
    import os
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, filename)
    print("📂 实际读取路径：", full_path)

    config = {}
    with open(full_path, 'r', encoding='utf-8') as f:  # 指定编码更保险
        for line in f:
            print("🔍 原始行内容：", line.strip())  # 增加调试
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config

print(read_db_config())
