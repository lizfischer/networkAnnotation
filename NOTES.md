### Setup
Setting up docker (note: there are some parts of this that aren't quite right)
https://www.jetbrains.com/guide/django/tutorials/django-docker/production-ready/

Polls tutorial:
https://docs.djangoproject.com/en/5.1/intro/tutorial03/


### modeling suggestion from steve
Noice. Use Postgres and consider models.JsonField for shit that's super dynamic. You have to write custom validators if you want to be super strict about types/values/etc in those cases, but it'll save you a shitload of work if you can put up with the hairy bits
Cuz you could have something like:

```
class Entitity(models.Model):
    name = models.CharField()
    allowed_properties = models.JsonField(default=list)

class EntityProperties(models.Model):
    entity = models.ForeignKey(Entity)
    property_values = models.JsonField(default=dict)
```
So `Entity.allowed_properties = ["name", "dob", "title", "sexiness"]` and then when you want to label an entity you have `EntityProperty(entity=e, property_values={"name": "me", "sexiness": "1000%"}`


### testing
https://docs.djangoproject.com/en/5.1/intro/tutorial05/
As long as your tests are sensibly arranged, they won’t become unmanageable. Good rules-of-thumb include having:
* a separate TestClass for each model or view
* a separate test method for each set of conditions you want to test
* test method names that describe their function
