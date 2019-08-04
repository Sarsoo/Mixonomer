import React, { Component } from "react";
const axios = require('axios');

class PlaylistView extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: this.props.match.params.name,
            parts: [],
            playlist_references: [],
            type: null,
            error: false,
            error_text: null,

            day_boundary: '',
            newPlaylistName: '',
            newPlaylistReference: '',

            shuffle: false
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleAddReference = this.handleAddReference.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemoveRow = this.handleRemoveRow.bind(this);
        this.handleRemoveRefRow = this.handleRemoveRefRow.bind(this);

        this.handleRun = this.handleRun.bind(this);

        this.handleShuffleChange = this.handleShuffleChange.bind(this);
    }

    componentDidMount(){
        this.getPlaylistInfo();
    }

    getPlaylistInfo(){
        axios.get(`/api/playlist?name=${ this.state.name }`)
            .then((response) => {
                this.setState(response.data);
            }).catch((error) => {
                this.setState({
                    error: true,
                    error_text: "error pulling playlist info"
                });
            });
    }

    handleInputChange(event){
        this.setState({
            [event.target.name]: event.target.value
        });

        if(event.target.name == 'day_boundary'){
            this.handleDayBoundaryChange(event.target.value);
        }
    }

    handleDayBoundaryChange(boundary) {
        axios.post('/api/playlist', {
            name: this.state.name,
            day_boundary: parseInt(boundary)
        }).catch((error) => {
            console.log(error);
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
            console.log(error);
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
                console.log(error);
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
                console.log(error);
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
            console.log(error);
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
            console.log(error);
        });
    }

    handleRun(event){
        axios.get('/api/playlist/run', {params: {name: this.state.name}})
        .catch((error) => {
            console.log(error);
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
                            <input type="text"
                                name="newPlaylistReference" 
                                className="full-width" 
                                value={this.state.newPlaylistReference} 
                                onChange={this.handleInputChange}
                                placeholder="managed playlist"></input>
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
                    { this.state.type == 'recents' &&
                     <tr>
                        <td className="center-text ui-text text-no-select">
                            day boundary
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