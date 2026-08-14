# from minio import Minio

# eos_client = Minio(
#     "mum-objectstore.e2enetworks.net",
#     # access_key="4NUE88K5WYDMGK1Z9I21",
#     # secret_key="4SQXWJDD62GJZA6YA24I9QHEDRLWYXJKUXWHZOHB",
#     # access_key="SXIFMBYIJW7R0IAXTKT9a",
#     # secret_key="HTQG6G3ENTQWOEJCRLDBIEGG6Q4GY71Q4AECGW5V",
#     access_key="O48CXRIMIVJITQAXC9SE",
#     secret_key="4Y18U2J6EIIUG89DJ4M0DPAFLJL5SRCBXZTDYHWZ",
#     secure=True,
# )

# # method: list_objects
# # params: bucket_name, prefix (object path prefix), recursive (set True for directories)

# objects = eos_client.list_objects("radian-dev", prefix="media/", recursive=False)


# print(objects)
# for obj in objects:
#     print(
#         obj.bucket_name, obj.object_name, obj.last_modified, obj.size, obj.content_type
#     )
