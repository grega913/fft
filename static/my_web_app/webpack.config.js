const path = require('path');

module.exports = {
  entry: {
    login: './login-auth1.js',  // Output: login.bundle.js
    main: './main1.js',        // Output: main.bundle.js
    firebaseConfig: './firebase-config.js', //output: firebaseConfig.bundle.js
    stripe: './stripe1.js'
  },
  output: {
    filename: '[name].bundle.js', // [name] will be replaced with the entry key
    path: path.resolve(__dirname, 'dist'),
  },
  mode: 'development', // or 'production'
};