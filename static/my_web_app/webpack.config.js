const path = require('path');

module.exports = {
  entry: {
    login: './js/login-auth.js',  // Output: login.bundle.js
    firebaseConfig: './js/firebase-config.js', //output: firebaseConfig.bundle.js
    stripe: './js/stripe.js'
  },
  output: {
    filename: '[name].bundle.js', // [name] will be replaced with the entry key
    path: path.resolve(__dirname, 'dist'),
  },
  mode: 'development', // or 'production'
};