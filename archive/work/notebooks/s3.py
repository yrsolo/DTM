import json
import time

import boto3

BUCKET = "dtm"
KEY = "snapshots/test/prep/default.json"
ENDPOINT_URL = "https://storage.yandexcloud.net"

session = boto3.session.Session()
s3 = session.client("s3", endpoint_url=ENDPOINT_URL)

t0 = time.perf_counter()
resp = s3.get_object(Bucket=BUCKET, Key=KEY)
t1 = time.perf_counter()

raw = resp["Body"].read()
t2 = time.perf_counter()

data = json.loads(raw.decode("utf-8"))
t3 = time.perf_counter()

size_mb = len(raw) / (1024 * 1024)

print(f"get_object: {(t1 - t0) * 1000:.1f} ms")
print(f"body.read:  {(t2 - t1) * 1000:.1f} ms")
print(f"json.loads: {(t3 - t2) * 1000:.1f} ms")
print(f"total:      {(t3 - t0) * 1000:.1f} ms")
print(f"size:       {size_mb:.2f} MiB")
print(f"type:       {type(data).__name__}")

# import json
# import statistics
# import time

# import boto3

# BUCKET = "dtm"
# KEY = "snapshots/test/prep/default.json"
# ENDPOINT_URL = "https://storage.yandexcloud.net"
# RUNS = 10

# s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)

# get_times = []
# read_times = []
# parse_times = []
# total_times = []
# sizes = []

# for i in range(RUNS):
#     t0 = time.perf_counter()
#     resp = s3.get_object(Bucket=BUCKET, Key=KEY)
#     t1 = time.perf_counter()

#     raw = resp["Body"].read()
#     t2 = time.perf_counter()

#     json.loads(raw.decode("utf-8"))
#     t3 = time.perf_counter()

#     get_times.append((t1 - t0) * 1000)
#     read_times.append((t2 - t1) * 1000)
#     parse_times.append((t3 - t2) * 1000)
#     total_times.append((t3 - t0) * 1000)
#     sizes.append(len(raw))

# print("get_object avg:", round(statistics.mean(get_times), 1), "ms")
# print("body.read  avg:", round(statistics.mean(read_times), 1), "ms")
# print("json.loads avg:", round(statistics.mean(parse_times), 1), "ms")
# print("total      avg:", round(statistics.mean(total_times), 1), "ms")
# print("size avg:", round(statistics.mean(sizes) / (1024 * 1024), 2), "MiB")
