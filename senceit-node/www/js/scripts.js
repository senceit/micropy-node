/**
 * Copyright 2020 - Intersect Technologies CC
 * SenceIt Web Configuration
 * Author: Niel Swart <niel@nielswwart.com>
 *
 */

var config = {
  in: {},
  out: {
    wifi: {
      ssid: "",
      password: "",
    },
    mqtt: {
      ip: "",
    },
    location: [0, 0],
    peripherals: {},
  },
};

$ = (function (t, e, n, i, o, r, s, u, c, f, l, h) {
  return (
    (h = function (t, e) {
      return new h.i(t, e);
    }),
    (h.i = function (i, o) {
      n.push.apply(
        this,
        i
          ? i.nodeType || i == t
            ? [i]
            : "" + i === i
            ? /</.test(i)
              ? (((u = e.createElement(o || "q")).innerHTML = i), u.children)
              : ((o && h(o)[0]) || e).querySelectorAll(i)
            : /f/.test(typeof i)
            ? /c/.test(e.readyState)
              ? i()
              : h(e).on("DOMContentLoaded", i)
            : i
          : n
      );
    }),
    (h.i[(l = "prototype")] = (h.extend = function (t) {
      for (f = arguments, u = 1; u < f.length; u++)
        if ((l = f[u])) for (c in l) t[c] = l[c];
      return t;
    })((h.fn = h[l] = n), {
      on: function (t, e) {
        return (
          (t = t.split(i)),
          this.map(function (n) {
            (i[(u = t[0] + (n.b$ = n.b$ || ++o))] = i[u] || []).push([e, t[1]]),
              n["add" + r](t[0], e);
          }),
          this
        );
      },
      off: function (t, e) {
        return (
          (t = t.split(i)),
          (l = "remove" + r),
          this.map(function (n) {
            if (((f = i[t[0] + n.b$]), (u = f && f.length)))
              for (; (c = f[--u]); )
                (e && e != c[0]) ||
                  (t[1] && t[1] != c[1]) ||
                  (n[l](t[0], c[0]), f.splice(u, 1));
            else !t[1] && n[l](t[0], e);
          }),
          this
        );
      },
      is: function (t) {
        return (
          (u = this[0]),
          (u.matches || u["webkit" + s] || u["moz" + s] || u["ms" + s]).call(
            u,
            t
          )
        );
      },
    })),
    h
  );
})(window, document, [], /\.(.+)/, 0, "EventListener", "MatchesSelector");

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
    console.log(path);
    this._createRequest(
      "POST",
      this.root + path,
      JSON.stringify(body) + "\n",
      callback
    );
  }
}

onDocumentReady(function () {
  const api = new API("http://192.168.4.1");

  const lon = $("#lon");
  lon.on("change", (event) => {
    config.out["location"][0] = event.target.value;
  });

  const lat = $("#lat");
  lat.on("change", (event) => {
    config.out["location"][1] = event.target.value;
  });

  const geo = navigator.geolocation;
  geo.getCurrentPosition((pos) => {
    const _lon = Number(pos.coords.longitude.toFixed(4));
    lon[0].value = _lon;
    config.out.location[0] = _lon;

    const _lat = Number(pos.coords.latitude.toFixed(4));
    lat[0].value = _lat;
    config.out.location[1] = _lat;
  });

  api.get("/config", (code, resp) => {
    config.in = resp;

    const saveAndRestartBtn = $("#saveAndRestartBtn");
    saveAndRestartBtn.on("click", () => {
      const res = confirm(`
      Are you sure you want to save and restart the device?

      The connection to this page will be lost and the device will
      reconnect to the configured Wifi Network.

      Ensure that your Wifi connection settings are correct`);
      if (res) {
        console.log("Rebooting device in 3s");
        setTimeout(() => {
          console.log("Calling API");
          api.post("/config", config.out, (code, resp) => {
            console.log(code);
            console.log(resp);
          });
        }, 3000);
      } else {
        console.log("Cancelling reboot...");
      }
    });

    const deviceId = $("#deviceId");
    deviceId.forEach((el) => (el.innerHTML = config.in.id));

    const wifiNetworks = $("#ssid");
    config.in["networks"].forEach((net) => {
      wifiNetworks[0].appendChild(
        $(`<option value="${net}">${net}</option>`)[0]
      );
    });
    wifiNetworks.on("change", (event) => {
      config.out["wifi"]["ssid"] = event.target.value;
    });

    const wifiPassword = $("#wifiPwd");
    wifiPassword.on("change", (event) => {
      config.out["wifi"]["password"] = event.target.value;
    });

    const showPassword = $("#showPwd");
    showPassword.on("click", (event) => {
      const checked = event.target.checked;
      if (checked) {
        wifiPassword[0].setAttribute("type", "text");
      } else {
        wifiPassword[0].setAttribute("type", "password");
      }
    });

    const controlIp = $("#ctrlIp");
    config.out.mqtt.ip = "senceit.local";
    controlIp[0].value = "senceit.local";
    controlIp.on("change", (event) => {
      config.out["mqtt"]["ip"] = event.target.value;
    });

    /**
     * Peripheral Configuration
     */
    const peripheralTable = $("#ioTable tbody");

    renderPeripheralTable(
      peripheralTable[0],
      Object.values(config.out.peripherals)
    );

    const addIoBtn = $("#addIoBtn");

    addIoBtn.on("click", () => {
      const max = Object.keys(config.in.pin_mapping).length;

      if (Object.keys(config.out.peripherals).length >= max) {
        alert(`You can add only ${max} peripheral(s) to this device`);
        return;
      }

      const configAnchor = $("#peripheralConfig");
      configAnchor[0].innerHTML = createPeripheralForm(
        Object.keys(config.in.peripherals)
      );

      const params = $("#params");
      const first =
        config.in.peripherals[Object.keys(config.in.peripherals)[0]];

      const prefix = `${config.in.topic_prefix[first.type]}/${config.in.id}/`;
      $("#mqtt_prefix")[0].innerHTML = prefix;
      $("#mqtt_topic")[0].value = first.config.topic;

      params[0].innerHTML = createPeripheralParams(
        Object.keys(first.config.parameters).map((k) => [
          toCapitalCase(k.replace("_", " ")),
          k,
          first.config.parameters[k].unit,
        ])
      );
      // selection change listener
      $("#peripheralName").on("change", (event) => {
        // TODO: Some additional work is needed here
        params[0].innerHTML = createPeripheralParams();
      });

      const saveBtn = $("#saveBtn");
      const cancelBtn = $("#cancelBtn");

      saveBtn.on("click", () => {
        const periph = $("#peripheralName")[0].value;
        const interval = $("#interval")[0].value;
        const topic = $("#mqtt_topic")[0].value;

        const selected = config.in.peripherals[periph];
        const parameters = selected.config.parameters;

        $("#params .row input").forEach((c) => {
          parameters[c.id].value = c.value;
        });

        // initialize peripherals
        const count = Object.keys(config.out.peripherals).length;
        config.out.peripherals[count.toString()] = {
          type: selected.type,
          name: periph,
          id: selected.id,
          config: {
            interval: interval,
            trigger: null,
            topic: prefix + topic,
            parameters: parameters,
          },
        };

        renderPeripheralTable(
          peripheralTable[0],
          Object.values(config.out.peripherals)
        );

        saveBtn.off("click");
        configAnchor[0].innerHTML = "";
      });

      cancelBtn.on("click", () => {
        cancelBtn.off("click");
        saveBtn.off("click");
        configAnchor[0].innerHTML = "";
      });
    });
  });
});

function renderPeripheralTable(table, peripherals) {
  table.innerHTML = peripherals.map((p) => createPeripheralRow(p)).join("");

  // Add listeners for peripheral events
  peripherals.forEach((p) => {
    let removeBtn = $(`#btn_${p.id}`);
    removeBtn.on("click", (event) => {
      const node = event.target.parentElement.parentNode;
      const id = node.id;
      table.removeChild(node);
      const key = Object.keys(config.out.peripherals).filter(
        (k) => config.out.peripherals[k].id === id
      )[0];
      delete config.out.peripherals[key];
    });
  });
}

function createPeripheralRow(peripheral) {
  return `
  <tr id="${peripheral.id}">
    <td>
      <div class="2 col" id="peripheralName">
        ${peripheral.name}
      </div>
    </td>
    <td>
      <div class="2 col">
      ${peripheral.config.interval}
      </div>
    </td>
    <td>
      <div class="2 col">
        ${peripheral.config.topic}
    </td>
    <td>
      <button class="btn btn-delete pull-right" id="btn_${peripheral.id}" type="button">DELETE</button>
    </td>
   </tr>`;
}

function createPeripheralForm(peripherals) {
  return `
    <div class="row">
      <div class="2 col">
        <select id="peripheralName" class="card">
          ${peripherals
            .map((p) => `<option value="${p}">${p}</option>`)
            .join("")}
        </select>
      </div>

      <div class="2 col">
        <select id="interval" class="card">
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
        <div class="row">
          <label id="mqtt_prefix" class="prepend"></label>
          <input
            class="card post"
            type="text"
            id="mqtt_topic"
            placeholder="MQTT Topic"
            pattern="(?=[^/].*)(\S*)"
            required
            title="MQTT Topics cannot start with an / or contain spaces"
            value="my/mqtt/topic"
          />
        </div>
      </div>
    </div>
    <div class="row pv2" id="params">
    </div>
    <div class="row">
      <button class="btn" id="cancelBtn" type="button">CANCEL</button>
      <button class="btn btn-success pull-right" id="saveBtn" type="button">SAVE</button>
    </div>
    `;
}

function createPeripheralParams(params) {
  return `
      ${params
        .map(
          (p) => `
          <div class="row">
            <label class="3 col">${p[0]}</label>
            <input type="text" class="3 col card" id="${p[1]}"> ${p[2]}
          </div>`
        )
        .join("")}
    `;
}

function toCapitalCase(str) {
  return str
    .split(" ")
    .map((sub) => sub.charAt(0).toUpperCase() + sub.substr(1))
    .join(" ");
}

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
