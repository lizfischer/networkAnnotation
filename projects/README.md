# EntityType Schema format
```json
{
  
}
```
# Field Types
## text
Any text

## number
Int or float

## date
YYYY-MM-DD

## geo
string with decimal `lat,long`

## list
List of strings

## bool
True/False

## entity
ID of a valid EntityType

# Example
## Schema 
```json
{
  "name": {"type": "text"},
  "age": {"type": "number"},
  "dob": {"type": "date"},
  "money": {"type": "number"},
  "location": {"type": "geo"},
  "fave color": {"type": "list", "options": ["red", "yellow", "blue"]},
  "cool": {"type": "bool"},
  "friend": {"type": "entity", "options": "2c688aa9-cd2a-4f6f-ae9e-fcd7b6b832ca"}
}
```

## Valid metadata
```json
{
  "name": "Liz",
  "age": 30,
  "dob": "1995-01-18",
  "money": 150.5,
  "location": "47.658779, -117.426048",
  "fave color": "blue",
  "cool": true,
  "friend": "d3fe0c57-29e4-433d-b691-5b6910142fdd"
}
```