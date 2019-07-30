import React, { Component } from "react";
const axios = require('axios');

class Index extends Component{

    constructor(props){
        super(props);
        this.state = {}
        // this.pingPlaylists();
    }

    pingPlaylists(){
        var self = this;
        axios.get('/api/playlists')
        .then((response) => {
            console.log(response)
        });
        axios.get('/api/user')
        .then((response) => {
            console.log(response)
        });
    }

    render(){
        return <p>index</p>;
    }
}

export default Index;