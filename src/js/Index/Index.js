import React, { Component } from "react";
const axios = require('axios');

class Index extends Component{

    constructor(props){
        super(props);
        this.state = {}
    }

    render(){
        return <h1 className="center-text text-no-select">welcome to playlist manager!</h1>;
    }
}

export default Index;