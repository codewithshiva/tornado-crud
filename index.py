import tornado.web
import tornado.ioloop
import os
import asyncpg
import asyncio

async def get_config():
    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "pool": await asyncpg.create_pool(PG_CONFIG['dsn'])
    }
    return settings

PG_CONFIG = {
    'user': 'postgres',
    'pass': '123456',
    'host': 'localhost',
    'database': 'formpg',
    'port': '5433'
}
PG_CONFIG['dsn'] = "postgres://%s:%s@%s:%s/%s" % (PG_CONFIG['user'], PG_CONFIG['pass'],
                                                  PG_CONFIG['host'], PG_CONFIG['port'], PG_CONFIG['database'])

# class basicRequestHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello,world !!!!!!")

class staticRequestHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.settings['template_path'])
        self.render("index.html")
    
class formRequestHandler(tornado.web.RequestHandler):
    async def post(self):
        # print(self.request.body)
        firstname = self.get_body_argument("firstname")
        lastname = self.get_body_argument("lastname")
        email = self.get_body_argument("email")
        city = self.get_body_argument("city")
    
        
        async with self.settings['pool'].acquire() as connection:    
            async with connection.transaction():
                update = '''
                        INSERT INTO employee1(firstname, lastname, email, city)  
                        VALUES($1, $2, $3, $4) 
                        '''
                await connection.execute(update, firstname, lastname, email, city)
                self.render("submit.html")
    
class resultRequestHandler(tornado.web.RequestHandler):
    async def get(self):
        action = self.get_argument('action', None)
        if action is None:
            self.render("result.html")
        elif action == 'fetch_result':
            async with self.settings['pool'].acquire() as connection: 
                rows = await connection.fetch("SELECT * FROM employee1")
                data = [dict(row) for row in rows]
                data = tornado.web.escape.json_encode(data)
                return self.write(data)
            
# async def main():
#     print(PG_CONFIG['dsn'])
#     async with self.settings['pool'].acquire() as connection:
#         async with connection.transaction():
#             new = '''
#                 CREATE TABLE employee1(
#                     firstName varchar(255),  
#                     lastName varchar(255),  
#                     email varchar(255),  
#                     city varchar(255)  
#                 );'''
#             await connection.execute(new)
            

if __name__ == "__main__":
    config = tornado.ioloop.IOLoop.current().run_sync(get_config)
    app = tornado.web.Application([
        # (r"/hello",basicRequestHandler),
        (r"/",staticRequestHandler),
        (r"/form",formRequestHandler),
        (r"/result",resultRequestHandler)
        
    ], **config)
    app.listen(8888)
    print("I'm listening on port 8888")
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    tornado.ioloop.IOLoop.current().start()

