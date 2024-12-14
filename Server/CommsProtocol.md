# Client-Server Communication Protocol
the client server communication we're using is socket based protocol, which means the server and client just send
bytes to one another, therefore, we need to create a format for the communication.
the format can change overtime, so we'll send the format each time a connection is established with a client.

## The format
There should be a basic format that will extend for each command individually.
> <blockquotetitle>Note</blockquotetitle><br>
> The protocol should contain keys for encryption and tokens. This is something to be thinking on.

### Basic client protocol
```json
{
  "Command": <Number>,
  "Data": <String>,
  "Checksum": <Number>
}
```

### Basic server protocol
```json
{
  "StatusCode": <Number>,
  "Status": <String>,
  "Data?": <String>,
  "Checksum": <Number>
}
```

<!-- Custom Styling -->
<style>
blockquote {
    border-left: 3px solid #599fff;
    background-color: transparent;
}

blockquote blockquotetitle {
    color: #599fff;
    font-size: 1.1em;
}
</style>