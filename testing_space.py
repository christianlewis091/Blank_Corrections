


fms = fmrest.Server('https://your-server.com',
                        user='admin',
                        password='admin',
                        database='Contacts',
                        layout='Contacts',
                        api_version='v1')
fms.login()
record = fms.get_record(1)
record.name
