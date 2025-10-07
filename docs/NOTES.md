### Setup
Setting up docker (note: there are some parts of this that aren't quite right)
https://www.jetbrains.com/guide/django/tutorials/django-docker/production-ready/

Polls tutorial:
https://docs.djangoproject.com/en/5.1/intro/tutorial03/

#### Starting docker
```
docker run build
docker compose up - d
```


### ERD
www.mermaidchart.com/app/projects/52552dd1-3c0e-4813-bead-71f7009e759b/diagrams/ca767d5e-1839-4563-acee-b45c7dea6c34

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


## Front-end
https://www.reddit.com/r/django/comments/1cvnciq/comment/l4s867d/?context=3


## validating metadata schemas
```
metadata = {"lat_field": "123,456", "height": 500, "email_address": "abc@def.com"}

def validate_metadata(metadata):
    validator_map = {
        "lat_field": [some_validation_func, other_validation_func],
        "height": [valid_height, is_posivite, is_not_zero],
    }

    for field_name, value in metadata.items():
         for validator in validator_map[field_name]:
               validator(value)  # These funcs raise ValueErrors OR return a list of them to collect later and combine
```
So I'm a big fan of the above pattern, you can explicitly lay out a list of fields and the ways they validate, and you have full control over which functions go in there. Then you just iterate over the whole dict, see what the field is, and run your validations on it.

Same for serialization, have a mapping + a func for each serialization to/from the DB and boom, you can change what the UI gets or sends without fucking with the underlying storage mechanism (though you CAN fuck with it too and keep parity)

You can even combine ALL of that shit into a class:

```
class FieldHelper:
    _field_mappings = {
        "field_name": {
            "validators": [],
            "serialize": lambda x: x,
            "deserialize": some_func,
       } # Etc
   }
```
And then that class has methods to `validate` `serialize` and `deserialize`

Yeah this would exist in its own place. BUT you can also import it into the model file and use it whenever fields are loaded or saved. So you can change the shape of the data that's store in the DB before you use it, and then change it back as you save it, and it's transparent to the DB. But again, you can also just save it however you want, it's a JSON field for a reason



