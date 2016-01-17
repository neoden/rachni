from config import Config, App
app = App()

print(app.root_path)
print(app.instance_path)

app.config.param1 = 'param1value'
print(app.config.param1)

app.config['PARAM2'] = 2
print(app.config['PARAM2'])