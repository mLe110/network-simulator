#include <iostream>
#include <fstream>

#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/assign.hpp>
#include <boost/optional.hpp>
#include <map>

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/ipv4-global-routing-helper.h"

#include "ns3/point-to-point-module.h"
#include "ns3/csma-module.h"
#include "ns3/wifi-module.h"

#include "ns3/mesh-helper.h"
#include "ns3/mesh-module.h"
#include "ns3/tap-bridge-module.h"
#include "ns3/bridge-module.h"

#include "ns3/mobility-module.h"

using namespace ns3;
namespace pt = boost::property_tree;

// helper classes
namespace sim {
enum NodeDeviceType {
	VM, CONTAINER, PROCESS, WIFI_AP, SWITCH, ROUTER
};

enum NetworkType {
	CSMA, AP_STA, ADHOC, P2P, MESH
};
}

class NodeDevice {
public:
	explicit NodeDevice(std::string pDeviceId, sim::NodeDeviceType pType) :
			deviceId(pDeviceId), type(pType) {
		node = CreateObject<Node>();
		if (type != sim::VM) {
			installInternetStack();
		}
	}
	virtual ~NodeDevice() {
	}

	virtual void setupDeviceOnNode(Ipv4AddressHelper &ipv4,
			Ptr<NetDevice> netDevice) = 0;
	virtual void printNode() = 0;

	Ptr<Node> getNode() {
		return node;
	}

	sim::NodeDeviceType getNodeDeviceType() {
		return type;
	}

protected:
	std::string deviceId;
	Ptr<Node> node;
	sim::NodeDeviceType type;

	void setNodePosition(Ptr<Node> node, float xpos, float ypos) {
		MobilityHelper mobility;
		Ptr<ListPositionAllocator> positionAlloc = CreateObject<
				ListPositionAllocator>();
		positionAlloc->Add(Vector(xpos, ypos, 0.0));
		mobility.SetPositionAllocator(positionAlloc);
		mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");

		mobility.Install(node);
	}

private:
	void installInternetStack() {
		InternetStackHelper stack;
		stack.Install(node);
	}
};

class TapNodeDevice: public NodeDevice {
public:
	TapNodeDevice(std::string deviceId, sim::NodeDeviceType type,
			std::string pTapName, float pXpos = 0.0, float pYpos = 0.0) :
			NodeDevice(deviceId, type), tapName(pTapName), xpos(pXpos), ypos(
					pYpos) {
	}

	void setupDeviceOnNode(Ipv4AddressHelper &ipv4, Ptr<NetDevice> netDevice) {
		std::string mode;

		if (type == sim::VM) {
			mode = "UseBridge";
		} else {
			mode = "ConfigureLocal";
			ipv4.Assign(netDevice);
		}

		if (xpos >= 0.0 && ypos >= 0.0) {
			setNodePosition(node, xpos, ypos);
		}

		TapBridgeHelper tapBridge;
		tapBridge.SetAttribute("DeviceName", StringValue(tapName));
		tapBridge.SetAttribute("Mode", StringValue(mode));
		tapBridge.Install(node, netDevice);
	}

	void printNode() {
		std::cout << "id: " << deviceId << ", tap: " << tapName << ", xpos: "
				<< xpos << ", ypos: " << ypos << std::endl;
	}

private:
	std::string tapName;
	float xpos;
	float ypos;
};

class ApNodeDevice: public NodeDevice {
public:
	ApNodeDevice(std::string deviceId, float pXpos, float pYpos) :
			NodeDevice(deviceId, sim::WIFI_AP), xpos(pXpos), ypos(pYpos) {
		assert(xpos >= 0.0 && ypos >= 0.0 && "AP node has invalid position.");
		setNodePosition(node, xpos, ypos);
	}

	void setupDeviceOnNode(Ipv4AddressHelper &ipv4, Ptr<NetDevice> netDevice) {
		ipv4.Assign(netDevice);
	}

	void printNode() {
		std::cout << "id: " << deviceId << ", xpos: " << xpos << ", ypos: "
				<< ypos << std::endl;
	}

private:
	float xpos;
	float ypos;
};

class SwitchNodeDevice: public NodeDevice {
public:
	SwitchNodeDevice(std::string deviceId) :
			NodeDevice(deviceId, sim::SWITCH) {
	}

	void setupDeviceOnNode(Ipv4AddressHelper &ipv4, Ptr<NetDevice> netDevice) {
		std::cout << "add device to switch" << std::endl;
		bridgeDevices.Add(netDevice);
	}
	void setupSwitch() {
		std::cout << "setup swtich" << std::endl;
		BridgeHelper bridge;
		bridge.Install(node, bridgeDevices);
	}

	void printNode() {
		std::cout << "id: " << deviceId << std::endl;
	}

private:
	NetDeviceContainer bridgeDevices;
};

class RouterNodeDevice: public NodeDevice {
public:
	RouterNodeDevice(std::string deviceId, float pXpos, float pYpos) :
			NodeDevice(deviceId, sim::ROUTER), xpos(pXpos), ypos(pYpos) {
		if (xpos >= 0.0 && ypos >= 0.0) {
			setNodePosition(node, xpos, ypos);
		}
	}

	void setupDeviceOnNode(Ipv4AddressHelper &ipv4, Ptr<NetDevice> netDevice) {
		ipv4.Assign(netDevice);
	}

	void printNode() {
		std::cout << "id: " << deviceId << ", xpos: " << xpos << ", ypos: "
				<< ypos << std::endl;
	}

private:
	float xpos;
	float ypos;
};

template<class T>
boost::optional<T> getValueFromJson(std::string key,
		pt::ptree::value_type &obj) {
	boost::optional<T> result;
	auto entry = obj.second.get_child_optional(key);
	if (entry)
		result = entry.get().get_value<T>();

	return result;
}

template<class T>
void getListValueFromJson(std::string key, pt::ptree::value_type &obj,
		std::list<T>& dataList) {
	for (pt::ptree::value_type& listObj : obj.second.get_child(key)) {
		dataList.push_back(listObj.second.get_value<T>());
	}
}

template<class K, class V>
void getMapValuesFromJson(std::string key, pt::ptree::value_type &obj,
		std::map<K, V>& dataMap) {
	auto entries = obj.second.get_child_optional(key);
	if (entries) {
		for (pt::ptree::value_type& mapEntry : entries.get()) {
			dataMap.insert(
					std::pair<std::string, std::string>(mapEntry.first,
							mapEntry.second.data()));
		}
	}
}

struct NetworkConfig {
	sim::NetworkType networkType;
	std::map<std::string, std::string> generalConfig;
	std::map<std::string, std::string> address;
	std::list<std::string> devices;
};

class JsonParser {
public:
	JsonParser(std::string topologyFile) {
		pt::read_json(topologyFile, root);
	}

	void createNodeDevices(std::map<std::string, NodeDevice*>& nodeDeviceMap) {
		NodeDevice *nodeDevice;

		for (pt::ptree::value_type &device : root.get_child("devices")) {
			std::string deviceId = getDeviceId(device);
			switch (getNodeDeviceType(device)) {
			case sim::WIFI_AP:
				nodeDevice = new ApNodeDevice(deviceId, getXPos(device),
						getYPos(device));
				break;
			case sim::ROUTER:
				nodeDevice = new RouterNodeDevice(deviceId, getXPos(device),
						getYPos(device));
				break;
			case sim::SWITCH:
				nodeDevice = new SwitchNodeDevice(deviceId);
				break;
			default:
				nodeDevice = new TapNodeDevice(deviceId,
						getNodeDeviceType(device), getTapIfName(device),
						getXPos(device), getYPos(device));
			}
			nodeDeviceMap.insert(
					std::pair<std::string, NodeDevice*>(deviceId, nodeDevice));
		}
	}

	void readNetworksJson(std::list<NetworkConfig> &networks) {
		for (pt::ptree::value_type& network : root.get_child("network")) {
			NetworkConfig networkConfig;
			networkConfig.networkType = getNetworkType(network);
			getMapValuesFromJson<std::string, std::string>("general_config",
					network, networkConfig.generalConfig);
			getMapValuesFromJson<std::string, std::string>("address", network,
					networkConfig.address);
			getListValueFromJson<std::string>("devices", network,
					networkConfig.devices);

			networks.push_back(networkConfig);
		}
	}

private:
	std::map<std::string, sim::NodeDeviceType> nodeDeviceTypeFromString =
			boost::assign::map_list_of("vm", sim::VM)("container",
					sim::CONTAINER)("process", sim::PROCESS)("ap", sim::WIFI_AP)(
					"switch", sim::SWITCH)("router", sim::ROUTER);
	std::map<std::string, sim::NetworkType> networkTypeFromString =
			boost::assign::map_list_of("CSMA", sim::CSMA)("AP_STA", sim::AP_STA)(
					"ADHOC", sim::ADHOC)("P2P", sim::P2P)("MESH", sim::MESH);
	pt::ptree root;

	sim::NodeDeviceType getNodeDeviceType(pt::ptree::value_type &dev) {
		std::string sType = getValueFromJson<std::string>("type", dev).get();
		return nodeDeviceTypeFromString.at(sType);
	}

	std::string getDeviceId(pt::ptree::value_type &dev) {
		return getValueFromJson<std::string>("device_id", dev).get();
	}

	float getXPos(pt::ptree::value_type &dev) {
		boost::optional<float> xpos = getValueFromJson<float>("xpos", dev);
		return xpos ? xpos.get() : (-std::numeric_limits<float>::max());
	}

	float getYPos(pt::ptree::value_type &dev) {
		boost::optional<float> ypos = getValueFromJson<float>("ypos", dev);
		return ypos ? ypos.get() : (-std::numeric_limits<float>::max());
	}

	std::string getTapIfName(pt::ptree::value_type &dev) {
		return getValueFromJson<std::string>("tap_if_name", dev).get();
	}

	sim::NetworkType getNetworkType(pt::ptree::value_type &dev) {
		std::string sType =
				getValueFromJson<std::string>("network_type", dev).get();
		return networkTypeFromString.at(sType);
	}
};

struct IpMappingData {
	std::string netmask;
	std::list<std::pair<NodeDevice*, Ptr<NetDevice>>> nodeNetDeviceList;
};

class NetworkHelper {
public:
	NetworkHelper(std::map<std::string, NodeDevice*> &pNodeDeviceMap) {
		nodeDeviceMap = pNodeDeviceMap;
		enableGlobalRouting = true;
	}

	void setupNetworkTopology(std::list<NetworkConfig> &networkConfig) {
		installAllNetworks(networkConfig);
		assignIpAddresses();
		setupNetworkSwitches();

		if (enableGlobalRouting) {
			Ipv4GlobalRoutingHelper::PopulateRoutingTables();
		}
	}

	void installAllNetworks(std::list<NetworkConfig> &networkConfig) {
		for (NetworkConfig &config : networkConfig) {
			installNetwork(config);
		}
	}

	void assignIpAddresses() {
		for (auto it = networkMapping.begin(); it != networkMapping.end();
				++it) {
			prepareAddressHelper(it->first, it->second.netmask);

			for (auto &nodeDevicePair : it->second.nodeNetDeviceList) {
				nodeDevicePair.first->setupDeviceOnNode(ipv4,
						nodeDevicePair.second);
			}
		}
	}

	void setupNetworkSwitches() {
		for (auto it = nodeDeviceMap.begin(); it != nodeDeviceMap.end(); ++it) {
			if (it->second->getNodeDeviceType() == sim::SWITCH) {
				dynamic_cast<SwitchNodeDevice*>(it->second)->setupSwitch();
			}
		}
	}

	void installNetwork(NetworkConfig &networkConfig) {
		switch (networkConfig.networkType) {
		case sim::P2P:
			setupPeerToPeerLinks(networkConfig);
			break;
		case sim::CSMA:
			setupCsmaLinks(networkConfig);
			break;
		case sim::AP_STA:
			setupApStaWifi(networkConfig);
			break;
		case sim::ADHOC:
			setupAdhocWifi(networkConfig);
			break;
		case sim::MESH:
			enableGlobalRouting = false;
			setupMesh(networkConfig);
			break;
		default:
			throw std::invalid_argument("Unknown network type.");
		}
	}

	void setupPeerToPeerLinks(NetworkConfig &networkConfig) {
		PointToPointHelper p2p;

		auto dataRate = getValueFromMapOptional(networkConfig.generalConfig,
				"data_rate");
		auto delay = getValueFromMapOptional(networkConfig.generalConfig,
				"delay");

		if (dataRate)
			p2p.SetDeviceAttribute("DataRate", StringValue(dataRate.get()));
		if (delay)
			p2p.SetChannelAttribute("Delay", StringValue(delay.get()));

		NodeContainer linkNodes;
		getNodesFromDeviceList(linkNodes, networkConfig.devices);

		NetDeviceContainer netDevices = p2p.Install(linkNodes);

		updateNodeDevices(netDevices, networkConfig.devices,
				networkConfig.address);
	}

	void setupCsmaLinks(NetworkConfig &networkConfig) {
		CsmaHelper csma;

		auto dataRate = getValueFromMapOptional(networkConfig.generalConfig,
				"data_rate");
		auto delay = getValueFromMapOptional(networkConfig.generalConfig,
				"delay");

		if (dataRate)
			csma.SetChannelAttribute("DataRate",
					DataRateValue(std::stoi(dataRate.get())));
		if (delay)
			csma.SetChannelAttribute("Delay",
					TimeValue(MilliSeconds(std::stoi(delay.get()))));

		NodeContainer linkNodes;
		getNodesFromDeviceList(linkNodes, networkConfig.devices);

		NetDeviceContainer netDevices = csma.Install(linkNodes);

		updateNodeDevices(netDevices, networkConfig.devices,
				networkConfig.address);

	}

	void setupApStaWifi(NetworkConfig &networkConfig) {
		YansWifiPhyHelper wifiPhy = YansWifiPhyHelper::Default();
		YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
		wifiPhy.SetChannel(wifiChannel.Create());

		Ssid ssid = Ssid(networkConfig.generalConfig.at("ssid"));
		WifiHelper wifi;
		WifiMacHelper wifiMac;
		wifi.SetRemoteStationManager("ns3::ArfWifiManager");

		NetDeviceContainer netDevices;

		for (std::string &deviceId : networkConfig.devices) {
			NodeDevice *nodeDevice = nodeDeviceMap.at(deviceId);

			if (nodeDevice->getNodeDeviceType() == sim::WIFI_AP) {
				wifiMac.SetType("ns3::ApWifiMac", "Ssid", SsidValue(ssid));
			} else {
				wifiMac.SetType("ns3::StaWifiMac", "Ssid", SsidValue(ssid),
						"ActiveProbing", BooleanValue(false));
			}

			netDevices.Add(
					wifi.Install(wifiPhy, wifiMac, nodeDevice->getNode()));
		}

		updateNodeDevices(netDevices, networkConfig.devices,
				networkConfig.address);
	}

	void setupAdhocWifi(NetworkConfig &networkConfig) {
		YansWifiPhyHelper wifiPhy = YansWifiPhyHelper::Default();
		YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
		wifiPhy.SetChannel(wifiChannel.Create());

		WifiHelper wifi;
		WifiMacHelper wifiMac;
		wifi.SetRemoteStationManager("ns3::ArfWifiManager");

		NodeContainer linkNodes;
		getNodesFromDeviceList(linkNodes, networkConfig.devices);

		NetDeviceContainer netDevices = wifi.Install(wifiPhy, wifiMac,
				linkNodes);
		updateNodeDevices(netDevices, networkConfig.devices,
				networkConfig.address);
	}

	void setupMesh(NetworkConfig &networkConfig) {
		YansWifiPhyHelper wifiPhy = YansWifiPhyHelper::Default();
		YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
		wifiPhy.SetChannel(wifiChannel.Create());

		MeshHelper mesh = MeshHelper::Default();
		mesh.SetStackInstaller("ns3::Dot11sStack");
		mesh.SetSpreadInterfaceChannels(MeshHelper::SPREAD_CHANNELS);
		mesh.SetMacType("RandomStart", TimeValue(Seconds(0.1)));

		NodeContainer linkNodes;
		getNodesFromDeviceList(linkNodes, networkConfig.devices);

		NetDeviceContainer netDevices = mesh.Install(wifiPhy, linkNodes);
		updateNodeDevices(netDevices, networkConfig.devices,
				networkConfig.address);
	}

private:
	std::map<std::string, NodeDevice*> nodeDeviceMap;
	std::map<std::string, IpMappingData> networkMapping;
	bool enableGlobalRouting;
	Ipv4AddressHelper ipv4;

	boost::optional<std::string> getValueFromMapOptional(
			std::map<std::string, std::string> &map, std::string key) {
		boost::optional<std::string> result;

		auto it = map.find(key);
		if (it != map.end())
			result = it->second;

		return result;
	}

	void getNodesFromDeviceList(NodeContainer &linkNodes,
			std::list<std::string> &devices) {
		for (std::string deviceId : devices) {
			linkNodes.Add(nodeDeviceMap.at(deviceId)->getNode());
		}
	}

	void updateNodeDevices(NetDeviceContainer &netDevices,
			std::list<std::string> &devices,
			std::map<std::string, std::string> &address) {
		int cnt = 0;
		std::string ip = prepareIpMappingMap(address);

		for (std::string deviceId : devices) {
			auto nodeDevice = nodeDeviceMap.at(deviceId);
			auto nodeDevicePair = std::pair<NodeDevice*, Ptr<NetDevice>>(
					nodeDevice, netDevices.Get(cnt));

			if (nodeDevice->getNodeDeviceType() == sim::WIFI_AP ||
					nodeDevice->getNodeDeviceType() == sim::ROUTER) {
				networkMapping.at(ip).nodeNetDeviceList.push_front(nodeDevicePair);
			} else {
				networkMapping.at(ip).nodeNetDeviceList.push_back(nodeDevicePair);
			}

			++cnt;
		}
	}

	std::string prepareIpMappingMap(
			std::map<std::string, std::string> &address) {
		auto oIp = getValueFromMapOptional(address, "ip");
		std::string ip = oIp ? oIp.get() : "-";

		if (networkMapping.find(ip) == networkMapping.end()) {
			IpMappingData ipData;
			auto oNetmask = getValueFromMapOptional(address, "netmask");
			ipData.netmask = oNetmask ? oNetmask.get() : "-";
			networkMapping.insert(
					std::pair<std::string, IpMappingData>(ip, ipData));
		}
		return ip;
	}

	void prepareAddressHelper(std::string ip, std::string netmask) {
		std::cout << "set ip: " << ip << std::endl;
		if (ip.compare("-") != 0) {
			ipv4.SetBase(Ipv4Address(ip.c_str()), Ipv4Mask(netmask.c_str()));
		}
	}
};

NS_LOG_COMPONENT_DEFINE("NetworkSimulatorCore");

int main(int argc, char *argv[]) {

	std::string topologyFile =
			"/app/network_topology.json";
	bool pyviz = false;

	CommandLine cmd;
	cmd.AddValue("topology", "Path to the network topology json file.",
			topologyFile);
	cmd.AddValue("pyviz",
			"Use VisualSimulatorImpl instead of realtime to visualize topology.",
			pyviz);
	cmd.Parse(argc, argv);

	if (pyviz) {
		GlobalValue::Bind("SimulatorImplementationType",
				StringValue("ns3::VisualSimulatorImpl"));
	} else {
		GlobalValue::Bind("SimulatorImplementationType",
				StringValue("ns3::RealtimeSimulatorImpl"));
	}
	GlobalValue::Bind("ChecksumEnabled", BooleanValue(true));
	PacketMetadata::Enable();

	// read network topology from json file
	JsonParser jsonParser(topologyFile);
	std::map<std::string, NodeDevice*> nodeDeviceMap;
	std::list<NetworkConfig> networkConfig;

	jsonParser.createNodeDevices(nodeDeviceMap);
	jsonParser.readNetworksJson(networkConfig);

	// create network topology & assign IP subnets
	NetworkHelper networkHelper(nodeDeviceMap);
	networkHelper.setupNetworkTopology(networkConfig);

	Simulator::Stop(Seconds(600.));
	Simulator::Run();
	Simulator::Destroy();
}

