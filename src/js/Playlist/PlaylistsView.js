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
        this.handleRunPlaylist = this.handleRunPlaylist.bind(this);
        this.handleDeletePlaylist = this.handleDeletePlaylist.bind(this);
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

    handleRunPlaylist(name, event){

    }

    handleDeletePlaylist(name, event){
        axios.delete('/api/playlist', { params: { name: name } })
        .then((response) => {
            this.getPlaylists();
        }).catch((error) => {
            console.log(error);
        });
    }

    render() {
        
        const table =   <div>
                            <Table playlists={this.state.playlists} 
                                handleRunPlaylist={this.handleRunPlaylist} 
                                handleDeletePlaylist={this.handleDeletePlaylist}/>
                        </div>;

        const loadingMessage = <p className="center-text">loading...</p>;

        return this.state.isLoading ? loadingMessage : table;
    }
}

function Table(props){
    return (
        <table className="app-table max-width">
            <tbody>
                { props.playlists.map((playlist) => <Row playlist={ playlist } 
                                                        handleRunPlaylist={props.handleRunPlaylist} 
                                                        handleDeletePlaylist={props.handleDeletePlaylist}
                                                        key={ playlist.name }/>) }
            </tbody>
        </table>
    );
}

function Row(props){
    return (
        <tr>
            <PlaylistLink playlist={props.playlist}/>
            <td style={{width: "100px"}}><button className="button" style={{width: "100px"}} onClick={(e) => props.handleRunPlaylist(props.playlist.name, e)}>run</button></td>
            <td style={{width: "100px"}}><button className="button"  style={{width: "100px"}} onClick={(e) => props.handleDeletePlaylist(props.playlist.name, e)}>delete</button></td>
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