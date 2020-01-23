from unittest import TestCase
from unittest.mock import patch, Mock

from network_simulator.exceptions.libvirt_network_service_exception import DuplicateNetworkNameException, \
    LibvirtNetworkCreationException, UnknownNetworkException, LibvirtHypervisorConnectionException
from network_simulator.network.libvirt_network_service import LibvirtNetworkService, NetworkInfo


@patch("network_simulator.network.libvirt_network_service.libvirt")
class TestLibvirtNetworkService(TestCase):
    def setUp(self):
        self.hypervisor_uri = "hypervisor:///system"
        self.libvirt_network = LibvirtNetworkService(self.hypervisor_uri)
        self.network_info_json = {
            "network_name": "testnet",
            "gateway_ip": "10.1.1.1",
            "netmask": "255.255.255.0",
            "start_ip": "10.1.1.40",
            "end_ip": "10.1.1.50"
        }

    def test_createNewConnection(self, mock_libvirt):
        mock_conn = Mock()
        mock_libvirt.open = mock_conn
        self.libvirt_network.conn = None
        self.libvirt_network.get_hypervisor_connection()
        mock_conn.assert_called_once()

    def test_getHypervisorConnectionWithExistingConn(self, mock_libvirt):
        mock_open = Mock()
        mock_conn = Mock()
        mock_libvirt.open = mock_open
        self.libvirt_network.conn = mock_conn
        conn = self.libvirt_network.get_hypervisor_connection()
        self.assertEqual(mock_conn, conn)
        mock_open.assert_not_called()

    def test_getHypervisorConnectionFails(self, mock_libvirt):
        mock_libvirt.open.return_value = None
        with self.assertRaises(LibvirtHypervisorConnectionException):
            self.libvirt_network.get_hypervisor_connection()

    def test_addNetworkSuccessfully(self, mock_libvirt):
        self.libvirt_network.add_network(self.network_info_json)
        self.assertIn(self.network_info_json["network_name"], self.libvirt_network.network_dict)

    def test_addNetworkWithCorrectValues(self, mock_libvirt):
        net_info = self.libvirt_network.add_network(self.network_info_json)
        self.assertEqual(self.network_info_json["network_name"], net_info.network_name)
        self.assertEqual(self.network_info_json["gateway_ip"], net_info.gateway_ip)
        self.assertEqual(self.network_info_json["netmask"], net_info.netmask)
        self.assertEqual(self.network_info_json["start_ip"], net_info.start_ip)
        self.assertEqual(self.network_info_json["end_ip"], net_info.end_ip)

    def test_addDuplicateNetwork(self, mock_libvirt):
        self.libvirt_network.add_network(self.network_info_json)
        with self.assertRaises(DuplicateNetworkNameException):
            self.libvirt_network.add_network(self.network_info_json)

    def test_addRemoveAddNetwork(self, mock_libvirt):
        self.libvirt_network.add_network(self.network_info_json)
        self.assertEqual(1, len(self.libvirt_network.network_dict))
        self.libvirt_network.remove_network(self.network_info_json["network_name"])
        self.assertEqual(0, len(self.libvirt_network.network_dict))
        self.libvirt_network.add_network(self.network_info_json)
        self.assertEqual(1, len(self.libvirt_network.network_dict))

    def test_createLibvirtConfig(self, mock_libvirt):
        network_info = NetworkInfo.from_network_dict(self.network_info_json)
        config_str = self.libvirt_network.create_libvirt_config_str(network_info)
        self.assertNotIn('{', config_str)
        self.assertNotIn('}', config_str)
        self.assertIn(network_info.network_name, config_str)
        self.assertIn(network_info.gateway_ip, config_str)
        self.assertIn(network_info.netmask, config_str)
        self.assertIn(network_info.start_ip, config_str)
        self.assertIn(network_info.end_ip, config_str)

    def test_createLibvirtNetworkFails(self, mock_libvirt):
        mock_conn = Mock()
        mock_libvirt.open.return_value = mock_conn
        mock_conn.networkCreateXML.return_value = None
        with self.assertRaises(LibvirtNetworkCreationException):
            self.libvirt_network.create_libvirt_network("valid config")

    def test_createLibvirtNetworkSuccessful(self, mock_libvirt):
        mock_network = Mock()
        mock_conn = Mock()
        mock_libvirt.open.return_value = mock_conn
        mock_conn.networkCreateXML.return_value = mock_network
        network = self.libvirt_network.create_libvirt_network("valid config")
        self.assertEqual(mock_network, network)

    def test_getLibvirtNetworkWithUnknownNetwork(self, mock_libvirt):
        self.libvirt_network.conn = Mock()
        self.libvirt_network.conn.networkLookupByName.return_value = None
        with self.assertRaises(UnknownNetworkException):
            self.libvirt_network.get_libvirt_network("invalid_network_name")

    def test_removeKnownNetwork(self, mock_libvirt):
        self.libvirt_network.add_network(self.network_info_json)
        self.assertEqual(1, len(self.libvirt_network.network_dict))
        self.libvirt_network.remove_network(self.network_info_json["network_name"])
        self.assertEqual(0, len(self.libvirt_network.network_dict))

    def test_removeUnknownNetwork(self, mock_libvirt):
        with self.assertRaises(KeyError):
            self.libvirt_network.remove_network(self.network_info_json["network_name"])



