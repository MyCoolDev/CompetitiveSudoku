# Client-Server Communication Protocol
the client server communication we're using is socket based protocol, which means the server and client just send
bytes to one another, therefore, we need to create a format for the communication.
the format can change overtime, so we'll send the format each time a connection is established with a client.

## The format
There should be a basic format that will extend for each command individually.

> [!Note]
> The protocol should contain keys for encryption and tokens. This is something to be thinking on.

## Basic client protocol
```json
{
  "Command": "<String>",
  "Data": "<Json>",
  "Checksum": "<String>"
}
```

## Basic server protocol
```json
{
  "StatusCode": "<Number>",
  "Status": "<String>",
  "Data?": "<Json>",
  "Checksum": "<String>"
}
```

## Register

#### The client request

```json
{
  "Command": "Register",
  "Data": {
    "Username": "<String>",
    "Password": "<String>"
  },
  "Checksum": "<String>"
}
```

#### The server response in case username or password are missing.

```json
{
  "StatusCode": 400,
  "Status": "Bad Request",
  "Data": {
    "Msg": "Missing Username or Password attribute."
  },
  "Checksum": "<String>"
}
```

#### The server response if username is not unique.

```json
{
  "StatusCode": 409,
  "Status": "Conflict",
  "Data": {
    "Msg": "Username must be unique."
  },
  "Checksum": "<String>"
}
```

#### The server response in successful registration.

```json
{
  "StatusCode": 201,
  "Status": "Created",
  "Data": {
    "Msg": "The new user has been registered."
  },
  "Checksum": "<String>"
}
```