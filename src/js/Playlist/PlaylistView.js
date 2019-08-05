import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

class PlaylistView extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: this.props.match.params.name,
            parts: [],
            playlists: [],
            playlist_references: [],
            type: null,

            day_boundary: '',
            recommendation_sample: '',
            newPlaylistName: '',
            newPlaylistReference: '',

            shuffle: false,
            include_recommendations: false
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddReference = this.handleAddReference.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemoveRow = this.handleRemoveRow.bind(this);
        this.handleRemoveRefRow = this.handleRemoveRefRow.bind(this);

        this.handleRun = this.handleRun.bind(this);

        this.handleShuffleChange = this.handleShuffleChange.bind(this);
        this.handleRecChange = this.handleRecChange.bind(this);
    }

    componentDidMount(){
        axios.all([this.getPlaylistInfo(), this.getPlaylists()])
        .then(axios.spread((info, playlists) => {
            
            info.data.parts.sort(function(a, b){
                if(a < b) { return -1; }
                if(a > b) { return 1; }
                return 0;
            });

            info.data.playlist_references.sort(function(a, b){
                if(a < b) { return -1; }
                if(a > b) { return 1; }
                return 0;
            });

            this.setState(info.data);
            this.setState({playlists: playlists.data.playlists});
        }))
        .catch((error) => {
            showMessage(`error getting playlist info (${error.response.status})`);
        });
    }

    getPlaylistInfo(){
        return axios.get(`/api/playlist?name=${ this.state.name }`);
    }

    getPlaylists(){
        return axios.get(`/api/playlists`);
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });

        if(event.target.name == 'day_boundary'){
            this.handleDayBoundaryChange(event.target.value);
        }
        if(event.target.name == 'recommendation_sample'){
            this.handleRecSampleChange(event.target.value);
        }
    }

    handleDayBoundaryChange(boundary) {
        axios.post('/api/playlist', {
            name: this.state.name,
            day_boundary: parseInt(boundary)
        }).catch((error) => {
            showMessage(`error updating boundary value (${error.response.status})`);
        });
    }

    handleRecSampleChange(sample){
        axios.post('/api/playlist', {
            name: this.state.name,
            recommendation_sample: parseInt(sample)
        }).catch((error) => {
            showMessage(`error updating rec. sample value (${error.response.status})`);
        });
    }

    handleShuffleChange(event) {
        this.setState({
            shuffle: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            shuffle: event.target.checked
        }).catch((error) => {
            showMessage(`error updating shuffle value (${error.response.status})`);
        });
    }

    handleRecChange(event) {
        this.setState({
            include_recommendations: event.target.checked
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            include_recommendations: event.target.checked
        }).catch((error) => {
            showMessage(`error updating rec. value (${error.response.status})`);
        });
    }

    handleAddPart(event){

        var check = this.state.parts.filter((e) => {
            return e == event.target.value;
        });

        if(check.length == 0) {
            var parts = this.state.parts.slice();
            parts.push(this.state.newPlaylistName);

            parts.sort(function(a, b){
                if(a < b) { return -1; }
                if(a > b) { return 1; }
                return 0;
            });

            this.setState({
                parts: parts,
                newPlaylistName: ''
            });
            axios.post('/api/playlist', {
                name: this.state.name,
                parts: parts
            }).catch((error) => {
                showMessage(`error adding part (${error.response.status})`);
            });
        }
    }

    handleAddReference(event){
        
        var check = this.state.playlist_references.filter((e) => {
            return e == event.target.value;
        });

        if(check.length == 0) {
            var playlist_references = this.state.playlist_references.slice();
            playlist_references.push(this.state.newPlaylistReference);
            
            playlist_references.sort(function(a, b){
                if(a < b) { return -1; }
                if(a > b) { return 1; }
                return 0;
            });
            
            this.setState({
                playlist_references: playlist_references,
                newPlaylistReference: ''
            });
            axios.post('/api/playlist', {
                name: this.state.name,
                playlist_references: playlist_references
            }).catch((error) => {
                showMessage(`error adding reference (${error.response.status})`);
            });
        }
    }

    handleRemoveRow(id, event){
        var parts = this.state.parts;
        parts = parts.filter(e => e !== id);
        this.setState({
            parts: parts
        });

        if(parts.length == 0) {
            parts = -1;
        }

        axios.post('/api/playlist', {
            name: this.state.name,
            parts: parts
        }).catch((error) => {
            showMessage(`error removing part (${error.response.status})`);
        });
    }

    handleRemoveRefRow(id, event){
        var playlist_references = this.state.playlist_references;
        playlist_references = playlist_references.filter(e => e !== id);
        this.setState({
            playlist_references: playlist_references
        });

        if(playlist_references.length == 0) {
            playlist_references = -1;
        }

        axios.post('/api/playlist', {
            name: this.state.name,
            playlist_references: playlist_references
        }).catch((error) => {
            showMessage(`error removing reference (${error.response.status})`);
        });
    }

    handleRun(event){
        axios.get('/api/playlist/run', {params: {name: this.state.name}})
        .then((reponse) => {
            showMessage(`${this.state.name} ran`);
        })
        .catch((error) => {
            showMessage(`error running ${this.state.name} (${error.response.status})`);
        });
    }

    render(){

        const table = (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.state.name }</h1></th>
                    </tr>
                </thead>
                { this.state.playlist_references.length > 0 && <ListBlock name="managed" handler={this.handleRemoveRefRow} list={this.state.playlist_references}/> }
                { this.state.parts.length > 0 && <ListBlock name="spotify" handler={this.handleRemoveRow} list={this.state.parts}/> }
                <tbody>
                    <tr>
                        <td>
                            <input type="text"
                                name="newPlaylistName" 
                                className="full-width" 
                                value={this.state.newPlaylistName} 
                                onChange={this.handleInputChange}
                                placeholder="spotify playlist"></input>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddPart}>add</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <select name="newPlaylistReference" 
                                    className="full-width"
                                    value={this.state.newPlaylistReference}
                                    onChange={this.handleInputChange}>
                                { this.state.playlists.map((entry) => <ReferenceEntry name={entry.name} key={entry.name} />) }
                            </select>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddReference}>add</button>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            shuffle output?
                        </td>
                        <td>
                            <input type="checkbox" 
                                checked={this.state.shuffle}
                                onChange={this.handleShuffleChange}></input>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            include recommendations?
                        </td>
                        <td>
                            <input type="checkbox" 
                                checked={this.state.include_recommendations}
                                onChange={this.handleRecChange}></input>
                        </td>
                    </tr>
                    <tr>
                        <td className="center-text ui-text text-no-select">
                            recommendations sample size
                        </td>
                        <td>
                        <input type="number" 
                                name="recommendation_sample"
                                className="full-width"
                                value={this.state.recommendation_sample}
                                onChange={this.handleInputChange}></input>
                        </td>
                    </tr>
                    { this.state.type == 'recents' &&
                     <tr>
                        <td className="center-text ui-text text-no-select">
                            added since (days)
                        </td>
                        <td>
                            <input type="number" 
                                name="day_boundary"
                                className="full-width"
                                value={this.state.day_boundary}
                                onChange={this.handleInputChange}></input>
                        </td>
                    </tr>  
                    }
                    <tr>
                        <td colSpan="2">
                            <button className="button full-width" onClick={this.handleRun}>run</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        );

        const error = <p style={{textAlign: "center"}}>{ this.state.error_text }</p>;

        return this.state.error ? error : table;
    }

}

function ReferenceEntry(props) {
    return (
        <option value={props.name}>{props.name}</option>
    );
}

function ListBlock(props) {
    return (
        <tbody>
            <tr><td colSpan="2" className="ui-text center-text text-no-select" style={{fontStyle: 'italic'}}>{props.name}</td></tr>
            { props.list.map((part) => <Row part={ part } key={ part } handler={props.handler}/>) }
        </tbody>
    );
}

function Row (props) {
    return (
        <tr>
            <td className="ui-text center-text text-no-select">{ props.part }</td>
            <td><button className="ui-text center-text button full-width" onClick={(e) => props.handler(props.part, e)}>remove</button></td>
        </tr>
    );
}

export default PlaylistView;