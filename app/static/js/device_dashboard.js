class Api {
  constructor (baseUrl) {
    this.baseUrl = baseUrl;
    this.requestBaseOpt = {
      cache: 'no-cache',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      },
    }
  }

  async get(path) {
    const opt = {};
    Object.assign(opt, this.requestBaseOpt);
    opt['method'] = 'GET';
    const resp = await fetch(this.baseUrl + '/' + path, opt);
    return await resp.json()
  }

}

class GlobalDeviceListener {
  constructor(hostname) {
    this.api = new Api('api');
    this.mqttClients = {};

    return (async () => {
      const brokerInfo = await this.api.get('broker/info');
      const {port} = brokerInfo.info;

      let urlSchema;
      if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
        urlSchema = 'ws';
      } else {
        urlSchema = 'wss';
      }

      this.mqttUrl = `${urlSchema}://${hostname}:${port}`;
      
      this.topicListeners = {};
      this.deviceIndicatorMap = {};
      this.accounts = {};

      // get all accounts from api
      let resp = await this.api.get('accounts');
      Object.assign(this.accounts, resp.accounts);

      const page_amount = resp.total / Object.keys(this.accounts).length;
      for (let i = 2; i < page_amount + 1; i++){
        resp = await this.api.get(`accounts?page=${i}`);
        Object.assign(this.accounts, resp.accounts);
      }

      // iterate over all users accounts
      for (const [mqttLogin, mqttPassword] of Object.entries(this.accounts)){
        const clientId = "browser-client-" + mqttLogin + '-' + uuidv4();
        const mqttClient = mqtt.connect(this.mqttUrl, {
          clientId: clientId,
          username: mqttLogin,
          password: mqttPassword,
          clean: false,
          connectTimeout: 4000,
        });

        // connect and subscribe
        mqttClient.on('connect', () => {
          console.log('connected', mqttLogin);
          const topic = mqttLogin + '/#';
          mqttClient.subscribe(topic, (err) => {
            if (err) {
              console.log('Error subscribe:', topic, err);
            }
          });
        });

        mqttClient.on('message', (topic, message) => {
          const [account, deviceType, deviceName, ...topicPath] = topic.split('/');
          this.#handleMessage(
            account,
            deviceType,
            deviceName,
            topicPath.join('/'),
            message.toString()
          );
        });
        this.topicListeners[mqttLogin] = {};
      }
      return this;
    })()
  }

  #handleMessage(account, deviceType, deviceName, topicPath, messageText) {
    const listener = this.topicListeners[account];

    if (!listener.hasOwnProperty(deviceType) || 
        !listener[deviceType].hasOwnProperty(deviceName) ||
        !listener[deviceType][deviceName].hasOwnProperty(topicPath)
    ){
      return;
    }

    listener[deviceType][deviceName][topicPath](messageText);
  }

  addTopicListener(topicPrefix, topicPath, callback){
    const {login, type, name} = topicPrefix;
    const listener = this.topicListeners[login];

    if(!listener.hasOwnProperty(type)){
      listener[type] = {};
    }

    if(!listener[type].hasOwnProperty(name)){
      listener[type][name] = {};
    }

    listener[type][name][topicPath] = callback;
  }
}


document.addEventListener("DOMContentLoaded", async (evt) => {
  const globalDeviceListener = await new GlobalDeviceListener(location.hostname);
  const devicesHTML = document.querySelector('.device-dashboard').children;
  
  for (let deviceColumn of devicesHTML){
    const accountLogin = deviceColumn.getAttribute('class').substring("account-".length);
    const deviceName = deviceColumn.querySelector('.device-name').getAttribute('name');
    const deviceType = deviceColumn.querySelector('.device-type').getAttribute('name');
    const indicatorHTML = deviceColumn.querySelector('.indicator');
    const offlineSVG = indicatorHTML.querySelector('.device-off');
    const onlineSVG = indicatorHTML.querySelector('.device-on');
    const unknowSVG = indicatorHTML.querySelector('.device-unknow')


    globalDeviceListener.addTopicListener({
      login: accountLogin,
      type: deviceType,
      name: deviceName,
    }, 'LWT', (msg) => {
      msg = msg.toLowerCase();
      unknowSVG.setAttribute('hidden', true);

      if(msg === 'offline'){
        onlineSVG.setAttribute('hidden', true);
        offlineSVG.removeAttribute('hidden');
      } else if (msg == 'online'){
        offlineSVG.setAttribute('hidden', true);
        onlineSVG.removeAttribute('hidden');
      }
    });

  }
});
