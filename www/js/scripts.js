class Peripheral {
  class;
  type;
  intervals;
}

class MqttConfig {
  ip;
  port;

  constructor(ip = "example.com", port = 1883) {
    this.ip = ip;
    this.port = port;
  }
}

class WifiConfig {
  ssid;
  password;
  constructor(ssid, password) {
    this.ssid = ssid;
    this.password = password;
  }
}

class DeviceConfig {
  wifi;
  mqtt;
  ios;

  constructor() {
    this.wifi = new WifiConfig();
    this.mqtt = new MqttConfig();
    this.ios = new Array();
  }

  addIO(io) {
    this.ios.push(io);
  }

  save(config, succesCallback) {
    // extract updated settings - it is automatically applied to this config
    $.ajax({
      type: "POST",
      url: "/config",
      data: JSON.stringify(config),
      dataType: "json",
      contentType: "application/json; charset=utf-8",
      success: succesCallback(config),
      error: function(e) {
        console.log("fail");
      }
    });
  }

  load() {
    // load config from device API
  }
}

class ConnectionComponent {
  WIFI_SSID = "ssid";
  WIFI_PWD = "wifiPwd";
  CTRL_IP = "ctrlIp";
  TOGGLE_PWD_CHECK = "showPwd";

  constructor(config) {
    this.config = config;
    this.id = "connectionComponent";
  }

  onInit() {
    document
      .getElementById(this.TOGGLE_PWD_CHECK)
      .addEventListener("click", this.togglePassword);
  }

  togglePassword() {
    let x = document.getElementById("showPwd");
    if (x.checked) {
      document.getElementById("wifiPwd").setAttribute("type", "text");
    } else {
      document.getElementById("wifiPwd").setAttribute("type", "password");
    }
  }

  render() {
    document
      .getElementById(this.WIFI_SSID)
      .setAttribute("value", this.config.wifi.ssid);

    document
      .getElementById(this.WIFI_PWD)
      .setAttribute("value", this.config.wifi.password);

    document
      .getElementById(this.CTRL_IP)
      .setAttribute("value", this.config.mqtt.ip);
  }

  getConnectionSettings() {
    this.config.wifi.ssid = document.getElementById(this.wifiSsid)[0].value;
    this.config.wifi.password = document.getElementById(
      this.wifiPassword
    )[0].value;
    this.config.mqtt.ip = document.getElementById(this.mqttIp)[0].value;

    return config;
  }
}

class ConfigurationComponent {
  ADD_BTN = "addBtn";
  PERIPHERAL_CLASS_TYPE = "classType";

  validIOs;
  constructor(config) {
    this.config = config;
    this.validIOs = new Array();
    this.id = "configComponent";
  }

  onInit() {
    document
      .getElementById(this.ADD_BTN)
      .addEventListener("click", this.addPeripheral);

    document
      .getElementById(this.PERIPHERAL_CLASS_TYPE)
      .addEventListener("change", function() {
        this.populateIOs(supportedIOs);
      });
  }

  getIOs() {
    switch (document.querySelector("#class_type")[0].selectedIndex) {
      case 0: {
        return {
          class: document.querySelector("#classType")[0].value,
          type: document.querySelector("#sensorType")[0].value,
          interval: document.querySelector("#sensor_interval")[0].value,
          topic: document.querySelector("#sensor_topic")[0].value
        };
      }
      case 1: {
        return {
          class: document.querySelector("#class_type")[0].value,
          type: document.querySelector("#sensorType")[0].value,
          interval: "",
          topic: document.querySelector("#sensor_topic")[0].value
        };
      }
    }
  }

  addIO(el, event) {
    if (document.querySelector("#sensor_topic")[0].checkValidity()) {
      this.config.addPeripheral(this.getPeripheral());
      this.renderPeripheralTable();
    } else {
      document.querySelector("#sensor_topic")[0].focus();
    }
  }

  populateIOs(supportedPeripherals) {
    const node = document.getElementById("sensorType");
    node.innerHTML = "";

    if (document.getElementById("classType")[0].value === "sensor") {
      for (let periph of this.validIOs.filter(p => p.class === "sensor")) {
        document.getElementById("sensorType").append("<option>");
        document
          .querySelector("#sensorType option")
          .eq(-1)
          .append(periph.type)
          .append("</option>");

        document.getElementById("sensor_interval").prop("disabled", false);
      }
    } else if (document.getElementById("classType")[0].value === "actuator") {
      for (let io of this.validIOs.filter(p => p.class === "actuator")) {
        document.getElementById("sensorType").append("<option>");
        document
          .querySelector("#sensorType option")
          .append(io.type)
          .append("</option>");

        document.querySelector("#sensor_interval").prop("disabled", true);
      }
    }
    document.querySelector("#sensorType").setAttribute("disabled", false);
    document.querySelector("#sensor_topic").setAttribute("disabled", false);
  }

  render() {
    // clear table
    const table = document.querySelector("#ioTable tbody");
    table.innerHTML = "";

    // Add peripherals to table
    for (let io of this.config.ios) {
      table.append("<tr></tr>"); // create a new row
      document
        .querySelector("#ioTable tbody tr")
        .eq(-1) // append to the last row (newly created one)
        .append("<td>" + io.class + "</td>")
        .append("<td>" + io.type + "</td>")
        .append("<td>" + io.interval + "</td>")
        .append("<td>" + io.topic + "</td>");
    }
  }
}

// load this from a json config file
const supportedIOs = [
  {
    class: "actuator",
    type: "SC-Relay"
  },
  {
    class: "sensor",
    type: "DHT",
    intervals: [""]
  }
];

class Page {
  components = new Array();
  CANCEL_BTN = "cancelBtn";
  SAVE_BTN = "saveBtn";

  constructor() {}

  save() {
    if ($("form")[0].checkValidity()) {
      this.config.save();
    } else {
      $("form :invalid")[0].focus();
    }
  }

  cancel(el, event) {
    this.config.load();
    this.render();
  }

  onInit() {
    document
      .getElementById(this.CANCEL_BTN)
      .addEventListener("click", this.cancel);

    document.getElementById(this.SAVE_BTN).addEventListener("click", this.save);

    this.components.forEach(c => {
      c.onInit();
    });
  }

  render() {
    this.components.forEach(c => {
      c.render();
    });
  }

  addComponent(component) {
    this.components.push(component);
  }
}

onDocumentReady(function() {
  device = new DeviceConfig();
  device.load();

  page = new Page();

  connect = new ConnectionComponent(device);
  config = new ConfigurationComponent(device);
  page.addComponent(connect);
  page.addComponent(config);

  page.onInit();
  page.render();
});

function onDocumentReady(fn) {
  // see if DOM is already available
  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    // call on next available tick
    setTimeout(fn, 1);
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}
