## Build Command

```
docker build -t qinbatista/ssrfargate .
```

## Run Command
```
docker run -itd -p 7000-7031:7000-7031 -p 7171:7171/udp   qinbatista/ssrfargate
```
## ssr.json
```
modify the password and port in this file
```


