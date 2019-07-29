import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

class PlaylistView extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: props.name
        }
    }

    render(){
        return <p>{this.state.name}</p>;
    }

}

export default PlaylistView