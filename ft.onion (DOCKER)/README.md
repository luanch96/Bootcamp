# ft_onion

# TODO

Tunear con shallot el hash que se genera


# Get started
You can deploy this project using Docker


![1](img/demo.gif)

## Docker

Let's use docker-compose to simplify the command.

```bash
chmod +x files/entrypoint.sh
chmod 600 files/id_rsa
```

```bash
docker-compose up
# [+] Running 1/1
#  - Container ft_onion-onion-nginx-1  Recreated                                                                                         0.2s 
# Attaching to ft_onion-onion-nginx-1
# ft_onion-onion-nginx-1  | [+] Initializing local clock
# ...
# ft_onion-onion-nginx-1  | Apr 19 17:29:50.000 [notice] Bootstrapped 75% (enough_dirinfo): Loaded enough directory info to build circuits
# ft_onion-onion-nginx-1  | Apr 19 17:29:50.000 [notice] Bootstrapped 90% (ap_handshake_done): Handshake finished with a relay to build circuits
# ft_onion-onion-nginx-1  | Apr 19 17:29:50.000 [notice] Bootstrapped 95% (circuit_create): Establishing a Tor circuit
# ft_onion-onion-nginx-1  | Apr 19 17:29:51.000 [notice] Bootstrapped 100% (done): Done
ft_onion-onion-nginx-1  | [+] Tor url:
ft_onion-onion-nginx-1  | j55eu2my2xpffid5bc2eysgvm3fxhfhqdw662bx6opxjli5svqx7fbad.onion
ft_onion-onion-nginx-1  | [+] QR Code Generated
```

* Copy *[+] Tor url:* onion domain. Every time that domain will be different.

* You can also check *hidden/qr.png* file generated when *docker-compose up* is executed.

A **user** (password auth. is disabled) is created during image setup. You can login using ssh as follows.

```bash
chmod 600 files/id_rsa
ssh -i files/id_rsa user@localhost -p 4242
...
Happy Hacking!
user@c1c95e1a2b49:~$
```

You are inside the container!
