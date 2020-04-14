var config = {
  in: {},
  out: {},
};

config.in = {
  id: "FB20GY",
  version: "0.1.0",
  arch: "esp8266",
  wifi: { ssid: "SenceIt" },
  mqtt: { ip: "senceit-ctrl" },
  location: (25.59877, -23.54654),
  peripherals: {
    LevelSensor: {
      id: "USLS01",
      type: "sensor",
      interval: "15m",
      trigger: null,
      topic: "dam/level",
      parameters: {
        dam_height: { measure: 1500, unit: "mm" },
        sensor_height: { measure: 1700, unit: "mm" },
        dam_diameter: { measure: 6, unit: "m" },
      },
    },
  },
  topic_prefix: { sensor: "stat", actuator: "cmnd" },
  pin_mapping: { USLS01: { trigger_pin: 14, echo_pin: 15 } },
};

class Binder {
  constructor() {
    this.listeners = new Array();
  }

  addElement(selector, prop) {
    const el = document.querySelector(selector);
    prop.addChangeListener((val) => {
      console.log(el);
      console.log(val);
      el.innerHTML = val;
    });
  }

  addListener(element, event, callback) {}
}

class Prop {
  constructor(value) {
    this.listeners = new Array();
    this.value = value;
  }

  addChangeListener(callback) {
    this.listeners.push(callback);
  }

  set(value) {
    this.value = value;
    this.listeners.forEach((l) => l(value));
  }

  get() {
    return this.value;
  }
}

class Updateable {
  constructor(selector) {
    this.prop = null;
    this.bf = new Binder();
    this.selector = selector;
  }

  set(value) {
    if (this.prop) {
      this.prop.set(value);
    } else {
      this.prop = new Prop(value);
      this.bf.addElement(this.selector, this.prop);
      this.prop.set(value);
    }
  }

  get() {
    return this.prop.get();
  }
}

class Peripheral {
  constructor() {
    this.type = "sensor";
    this.name = "LevelSensor";
    this.intervals = [];
  }
}

class MqttConfig {
  constructor(ip = "example.com", port = 1883) {
    this.ip = ip;
    this.port = port;
  }
}

class WifiConfig {
  constructor(ssid, password) {
    this.ssid = ssid;
    this.password = password;
  }
}

class DeviceConfig {
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
    // $.ajax({
    //   type: "POST",
    //   url: "/config",
    //   data: JSON.stringify(config),
    //   dataType: "json",
    //   contentType: "application/json; charset=utf-8",
    //   success: succesCallback(config),
    //   error: function (e) {
    //     console.log("fail");
    //   },
    // });
  }

  load() {
    // load config from device API
  }
}

class API {
  constructor(root) {
    this.root = root;
    this.mime_type = "application/json";
  }

  _createRequest(method, url, body, callback) {
    const httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = this._wrapCallback(httpRequest, callback);
    httpRequest.open(method, url);
    httpRequest.setRequestHeader("Content-Type", this.mime_type);

    if (body) {
      httpRequest.send(body);
    } else {
      httpRequest.send();
    }
  }

  _wrapCallback(httpReq, callback) {
    return function () {
      if (httpReq.readyState === XMLHttpRequest.DONE) {
        if (httpReq.status === 200) {
          const resp = JSON.parse(httpReq.responseText);
          callback(httpReq.status, resp);
        } else {
          // There was a problem with the request.
        }
      } else {
        // Not ready yet.
      }
    };
  }

  get(path, callback) {
    this._createRequest("GET", this.root + path, null, callback);
  }

  post(path, body, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
      if (this.readyState == 4) {
        if (this.status == 200) {
          document.getElementById("status").innerHTML = this.responseText;
        } else {
          document.getElementById("status").innerHTML = "Disconnected";
        }
      }
    };

    function powerSwitch() {
      xhttp.open("GET", "/switch", true);
      xhttp.send();
    }
  }

  put(path, body, callback) {}

  delete(path, callback) {}
}

class ConnectionComponent {
  constructor(config, api) {
    this.config = config;
    this.id = "connectionComponent";
    this.api = api;

    // selectors
    this.WIFI_SSID = "ssid";
    this.WIFI_PWD = "wifiPwd";
    this.CTRL_IP = "ctrlIp";
    this.LON = "lon";
    this.LAT = "lat";
    this.TOGGLE_PWD_CHECK = "showPwd";
    this.networks = Array();
  }

  onInit() {
    document
      .getElementById(this.TOGGLE_PWD_CHECK)
      .addEventListener("click", ($event) => {
        const x = document.getElementById("showPwd");
        if (x.checked) {
          document.getElementById(this.WIFI_PWD).setAttribute("type", "text");
        } else {
          document
            .getElementById(this.WIFI_PWD)
            .setAttribute("type", "password");
        }
      });

    document
      .getElementById(this.WIFI_SSID)
      .addEventListener("change", ($event) => {
        this.config.wifi.ssid = $event.target.selectedOptions[0].value;
      });

    document
      .getElementById(this.WIFI_PWD)
      .addEventListener("input", ($event) => {
        this.config.wifi.password = $event.target.value;
      });

    document
      .getElementById(this.CTRL_IP)
      .addEventListener("input", ($event) => {
        this.config.mqtt.ip = $event.target.value;
      });

    this.populateSsids();
    this.setDefaultLocation();
  }

  render() {
    if (this.config.wifi.password) {
      document
        .getElementById(this.WIFI_PWD)
        .setAttribute("value", this.config.wifi.password);
    }

    if (this.config.wifi.ssid) {
      console.log("Selecting the correct wifi ssid");
    }

    document
      .getElementById(this.CTRL_IP)
      .setAttribute("value", this.config.mqtt.ip);
  }

  populateSsids() {
    const select = document.getElementById(this.WIFI_SSID);
    // let resp = {};
    // resp["networks"] = ["Swart", "Swart", "Swart-LTE"];
    this.api.get("/config", (code, resp) => {
      for (let net of resp["networks"]) {
        const el = document.createElement("option");
        el.text = net;
        el.value = net;
        select.add(el);
      }
    });
  }

  setDefaultLocation() {
    const geo = navigator.geolocation;
    geo.getCurrentPosition((pos) => {
      document.getElementById(this.LON).value = pos.coords.longitude;
      document.getElementById(this.LAT).value = pos.coords.latitude;
    });
  }

  getConnectionSettings() {
    return this.config;
  }
}

class ConfigurationComponent {
  constructor(config) {
    this.config = config;
    this.validIOs = new Array();
    this.id = "configComponent";
    this.ADD_BTN = "addBtn";
    this.PERIPHERAL_CLASS_TYPE = "classType";
  }

  onInit() {
    document.getElementById(this.ADD_BTN).addEventListener("click", this.addIO);

    document
      .getElementById(this.PERIPHERAL_CLASS_TYPE)
      .addEventListener("change", function () {
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
          topic: document.querySelector("#sensor_topic")[0].value,
        };
      }
      case 1: {
        return {
          class: document.querySelector("#class_type")[0].value,
          type: document.querySelector("#sensorType")[0].value,
          interval: "",
          topic: document.querySelector("#sensor_topic")[0].value,
        };
      }
    }
  }

  addIO(el, event) {
    // if (document.querySelector("#sensor_topic")[0].checkValidity()) {
    //   this.config.addPeripheral(this.getPeripheral());
    //   this.renderPeripheralTable();
    // } else {
    //   document.querySelector("#sensor_topic")[0].focus();
    // }

    let per = new PeripheralComponent();
    per.render();
  }

  populateIOs(supportedPeripherals) {
    const node = document.getElementById("sensorType");
    node.innerHTML = "";

    if (document.getElementById("classType")[0].value === "sensor") {
      for (let periph of this.validIOs.filter((p) => p.class === "sensor")) {
        document.getElementById("sensorType").append("<option>");
        document
          .querySelector("#sensorType option")
          .eq(-1)
          .append(periph.type)
          .append("</option>");

        document.getElementById("sensor_interval").prop("disabled", false);
      }
    } else if (document.getElementById("classType")[0].value === "actuator") {
      for (let io of this.validIOs.filter((p) => p.class === "actuator")) {
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

class PeripheralComponent {
  onInit() {
    document
      .getElementById(this.ADD_BTN)
      .addEventListener("click", this.addPeripheral);

    document
      .getElementById(this.PERIPHERAL_CLASS_TYPE)
      .addEventListener("change", function () {
        this.populateIOs(supportedIOs);
      });
  }

  render() {
    document.getElementById("peripherals").insertAdjacentHTML(
      "beforeend",
      `
    <div class="row">
      <div class="2 col">
        <select id="classType" class="card">
          <option value="sensor">Sensor</option>
          <option value="actuator">Actuator</option>
        </select>
      </div>
      <div class="2 col">
        <select id="sensorType" class="card" disabled="true">
          {" "}
        </select>
      </div>
      <div class="2 col">
        <select id="sensor_interval" class="card" disabled="true">
          <option value="1m">1 Minute</option>
          <option value="5m">5 Minutes</option>
          <option value="10m">10 Minutes</option>
          <option value="30m">30 Minutes</option>
          <option value="1h">1 Hour</option>
          <option value="6h">12 Hours</option>
          <option value="24h">24 Hours</option>
        </select>
      </div>
      <div class="2 col">
        <input
          class="card"
          type="text"
          id="sensor_topic"
          placeholder="MQTT Topic"
          disabled="true"
          pattern="(?=[^/].*)(\S*)"
          required
          title="MQTT Topics cannot start with an / or contain spaces"
          value="my/mqtt/topic"
        />
      </div>
    </div>`
    );
  }
}

class Page {
  constructor(api) {
    this.components = new Array();
    this.CANCEL_BTN = "cancelBtn";
    this.SAVE_BTN = "saveBtn";
  }

  save() {
    // save config
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

    this.components.forEach((c) => {
      c.onInit();
    });
  }

  render() {
    this.components.forEach((c) => {
      c.render();
    });
  }

  addComponent(component) {
    this.components.push(component);
  }
}

onDocumentReady(function () {
  const device = new DeviceConfig();
  device.load();

  const page = new Page();
  const api = new API("http://10.0.0.125");

  // const connect = new ConnectionComponent(device, api);
  // const conf = new ConfigurationComponent(device);

  const deviceId = new Updateable("#deviceId");
  deviceId.set(config.in.id);

  // page.addComponent(connect);
  // page.addComponent(conf);

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
