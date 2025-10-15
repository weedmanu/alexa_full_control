"""
Découverte réseau des appareils Alexa sur le LAN.

Ce module permet de scanner le réseau local pour trouver les appareils Echo
et tenter d'accéder à leurs API locales.

Auteur: M@nu
Date: 12 octobre 2025
"""

import socket
import json
from typing import Optional, List, Dict, Any
from loguru import logger
from utils.logger import SharedIcons


class AlexaNetworkDiscovery:
    """
    Découverte et interaction avec les API locales des appareils Alexa.
    
    Les appareils Echo exposent plusieurs services sur le réseau local :
    - UPnP/SSDP pour la découverte automatique
    - API HTTP locale sur certains ports (potentiellement)
    - mDNS/Bonjour pour les noms .local
    
    Exemple:
        >>> discovery = AlexaNetworkDiscovery()
        >>> devices = discovery.discover_upnp()
        >>> for device in devices:
        ...     print(f"Found: {device['name']} at {device['ip']}")
    """

    # Ports connus utilisés par les appareils Echo
    COMMON_PORTS = [
        80,      # HTTP standard
        443,     # HTTPS standard
        8080,    # HTTP alternatif
        8443,    # HTTPS alternatif
        1900,    # UPnP/SSDP
        5353,    # mDNS
        55443,   # Parfois utilisé par Amazon
    ]

    # Endpoints API locaux potentiels
    LOCAL_ENDPOINTS = [
        "/api/status",
        "/api/device",
        "/api/calendar",
        "/api/events",
        "/setup",
        "/settings",
        "/_setup",
    ]

    def __init__(self):
        """Initialise le scanner réseau."""
        logger.debug("AlexaNetworkDiscovery initialisé")

    def discover_upnp(self, timeout: int = 5) -> List[Dict[str, Any]]:
        """
        Découvre les appareils Alexa via UPnP/SSDP.

        Args:
            timeout: Temps d'attente en secondes

        Returns:
            Liste des appareils découverts avec leurs infos

        Example:
            >>> devices = discovery.discover_upnp(timeout=10)
            >>> print(f"Trouvé {len(devices)} appareils")
        """
        try:
            logger.info(f"{SharedIcons.SEARCH} Découverte UPnP/SSDP (timeout={timeout}s)...")

            # Message SSDP M-SEARCH
            ssdp_request = (
                "M-SEARCH * HTTP/1.1\r\n"
                "HOST: 239.255.255.250:1900\r\n"
                "MAN: \"ssdp:discover\"\r\n"
                "MX: 3\r\n"
                "ST: upnp:rootdevice\r\n"
                "\r\n"
            )

            # Créer socket UDP multicast
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

            # Envoyer la requête SSDP
            sock.sendto(ssdp_request.encode(), ("239.255.255.250", 1900))

            devices = []
            seen_ips = set()

            # Recevoir les réponses
            while True:
                try:
                    data, addr = sock.recvfrom(65507)
                    response = data.decode('utf-8', errors='ignore')

                    # Filtrer les appareils Amazon/Echo
                    if any(keyword in response.lower() for keyword in ['amazon', 'echo', 'alexa']):
                        ip = addr[0]
                        if ip not in seen_ips:
                            seen_ips.add(ip)
                            device_info = self._parse_ssdp_response(response, ip)
                            devices.append(device_info)
                            logger.info(f"  {SharedIcons.DEVICE} Trouvé: {ip} - {device_info.get('server', 'Unknown')}")

                except socket.timeout:
                    break
                except Exception as e:
                    logger.debug(f"Erreur réception SSDP: {e}")
                    continue

            sock.close()

            logger.success(f"{SharedIcons.SUCCESS} {len(devices)} appareil(s) Alexa découvert(s)")
            return devices

        except Exception:
            logger.exception("Erreur lors de la découverte UPnP")
            return []

    def _parse_ssdp_response(self, response: str, ip: str) -> Dict[str, Any]:
        """
        Parse une réponse SSDP.

        Args:
            response: Réponse SSDP brute
            ip: Adresse IP de l'appareil

        Returns:
            Dictionnaire avec les infos extraites
        """
        info = {"ip": ip}

        # Parser les headers HTTP
        for line in response.split('\r\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if key == 'server':
                    info['server'] = value
                elif key == 'location':
                    info['location'] = value
                elif key == 'usn':
                    info['usn'] = value
                elif key == 'st':
                    info['service_type'] = value

        return info

    def scan_device_ports(self, ip: str, ports: Optional[List[int]] = None) -> Dict[int, bool]:
        """
        Scanne les ports d'un appareil.

        Args:
            ip: Adresse IP de l'appareil
            ports: Liste des ports à scanner (utilise COMMON_PORTS si None)

        Returns:
            Dictionnaire {port: is_open}

        Example:
            >>> open_ports = discovery.scan_device_ports("192.168.1.100")
            >>> print(f"Ports ouverts: {[p for p, o in open_ports.items() if o]}")
        """
        if ports is None:
            ports = self.COMMON_PORTS

        logger.debug(f"{SharedIcons.SEARCH} Scan des ports sur {ip}...")

        results = {}
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            try:
                result = sock.connect_ex((ip, port))
                is_open = (result == 0)
                results[port] = is_open

                if is_open:
                    logger.debug(f"  {SharedIcons.SUCCESS} Port {port} ouvert")

            except Exception as e:
                logger.debug(f"  {SharedIcons.ERROR} Port {port} erreur: {e}")
                results[port] = False
            finally:
                sock.close()

        return results

    def test_local_api(self, ip: str, port: int = 80) -> Dict[str, Any]:
        """
        Teste les endpoints API locaux sur un appareil.

        Args:
            ip: Adresse IP de l'appareil
            port: Port HTTP à tester

        Returns:
            Résultats des tests d'endpoints

        Example:
            >>> results = discovery.test_local_api("192.168.1.100")
            >>> for endpoint, data in results.items():
            ...     if data.get('status') == 200:
            ...         print(f"{SharedIcons.SUCCESS} {endpoint} accessible!")
        """
        import requests

        logger.info(f"{SharedIcons.SEARCH} Test API locale sur {ip}:{port}...")

        results = {}

        for endpoint in self.LOCAL_ENDPOINTS:
            url = f"http://{ip}:{port}{endpoint}"

            try:
                response = requests.get(url, timeout=3)

                results[endpoint] = {
                    "status": response.status_code,
                    "size": len(response.content),
                    "content_type": response.headers.get("Content-Type", ""),
                }

                if response.status_code == 200:
                    logger.info(f"  {SharedIcons.SUCCESS} {endpoint} → {response.status_code}")
                    try:
                        results[endpoint]["data"] = response.json()
                    except:
                        results[endpoint]["text"] = response.text[:500]
                else:
                    logger.debug(f"  {SharedIcons.WARNING} {endpoint} → {response.status_code}")

            except requests.exceptions.Timeout:
                results[endpoint] = {"error": "timeout"}
            except requests.exceptions.ConnectionError:
                results[endpoint] = {"error": "connection_refused"}
            except Exception as e:
                results[endpoint] = {"error": str(e)}

        return results

    def find_device_by_serial(self, serial: str, subnet: str = "192.168.1") -> Optional[str]:
        """
        Tente de localiser un appareil par son numéro de série via mDNS/Bonjour.

        Args:
            serial: Numéro de série de l'appareil
            subnet: Sous-réseau à scanner (ex: "192.168.1")

        Returns:
            Adresse IP si trouvée, None sinon

        Example:
            >>> ip = discovery.find_device_by_serial("G6G2MM125193038X")
            >>> if ip:
            ...     print(f"Salon Echo trouvé à {ip}")
        """
        logger.info(f"{SharedIcons.SEARCH} Recherche de l'appareil {serial[:8]}... sur {subnet}.0/24")

        # Essayer mDNS d'abord
        try:
            hostname = f"{serial.lower()}.local"
            ip = socket.gethostbyname(hostname)
            logger.success(f"{SharedIcons.SUCCESS} Trouvé via mDNS: {ip}")
            return ip
        except socket.gaierror:
            logger.debug(f"mDNS échoué pour {hostname}")

        # Fallback: scan du sous-réseau (lent!)
        # TODO: Implémenter un scan ARP rapide
        logger.log("WARNING", "Scan complet du sous-réseau non implémenté (trop lent)")

        return None
