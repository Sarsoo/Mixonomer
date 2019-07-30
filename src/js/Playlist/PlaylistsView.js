import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
const axios = require('axios');

class PlaylistsView extends Component {

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
        <table className="app-table max-width">
            <tbody>
                { props.playlists.map((playlist) => <Row playlist={ playlist } key={ playlist.name }/>) }
            </tbody>
        </table>
    );
}

function Row(props){
    return (
        <tr>
            <PlaylistLink playlist={props.playlist}/>
        </tr>
    );
}

function PlaylistLink(props){
    return (
        <td>
            <Link to={ getPlaylistLink(props.playlist.name) } className="button full-width">{ props.playlist.name }</Link>
        </td>
    );
}

function getPlaylistLink(playlistName){
    return '/app/playlist/' + playlistName;
}

export default PlaylistsView;