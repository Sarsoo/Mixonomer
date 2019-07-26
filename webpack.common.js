const path = require('path');
const webpack = require('webpack');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
	entry: {
	    app: './src/js/app.js'
	    },
	module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /(node_modules|bower_components)/,
        loader: "babel-loader",
        options: { presets: ["@babel/env"] }
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      }
    ]
    },
    plugins: [
        new CleanWebpackPlugin()
    ],
    resolve: { extensions: ["*", ".js", ".jsx"] },
	output: {
		filename: '[name].bundle.js',
		path: path.resolve(__dirname, 'build/js')
	}
};
