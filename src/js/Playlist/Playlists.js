import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

class Playlists extends Component {

    constructor(props){
        super(props);
        this.state = {
            isLoading: true
        }
        this.getPlaylists();
    }

    getPlaylists(){
        var self = this;
        axios.get('/api/playlists')
        .then((response) => {
            self.setState({
                playlists: response.data.playlists,
                isLoading: false
            });
        });
    }

    render() {
        
        const table = <div><Table playlists={this.state.playlists}/></div>;
        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function Table(props){
    return (
        <div>
            { props.playlists.map((playlist) => <Row playlist={ playlist } key={ playlist.name }/>) }
        </div>
    );
}

function Row(props){
    return (
        <PlaylistLink playlist={props.playlist}/>
    );
}

function PlaylistLink(props){
    return (
        <Link to={ getPlaylistLink(props.playlist.name) }>{ props.playlist.name }</Link>
    );
}

function getPlaylistLink(playlistName){
    return '/app/playlist/' + playlistName;
}

export default Playlists;