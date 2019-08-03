import React, { Component } from "react";
const axios = require('axios');

class PlaylistView extends Component{

    constructor(props){
        super(props);
        this.state = {
            name: this.props.match.params.name,
            parts: [],
            type: null,
            error: false,
            error_text: null,

            day_boundary: '',
            newPlaylistName: '',

            shuffle: false
        }
        this.handleAddPart = this.handleAddPart.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleRemoveRow = this.handleRemoveRow.bind(this);

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
            day_boundary: boundary
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
        var parts = this.state.parts;
        parts.push(this.state.newPlaylistName);
        this.setState({
            parts: parts,
            add_part_value: ''
        });
        axios.post('/api/playlist', {
            name: this.state.name,
            parts: parts
        }).catch((error) => {
            console.log(error);
        });
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

    render(){

        const table = (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.state.name }</h1></th>
                    </tr>
                </thead>
                <tbody>
                    { this.state.parts.map((part) => <Row part={ part } key={ part } handler={this.handleRemoveRow}/>) }
                    <tr>
                        <td>
                            <input type="text"
                                name="newPlaylistName" 
                                className="full-width" 
                                value={this.state.newPlaylistName} 
                                onChange={this.handleInputChange}
                                placeholder="new playlist"></input>
                        </td>
                        <td>
                            <button className="button full-width" onClick={this.handleAddPart}>add</button>
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
                            <input type="text" 
                                name="day_boundary"
                                className="full-width"
                                value={this.state.day_boundary}
                                onChange={this.handleInputChange}></input>
                        </td>
                    </tr>  
                    }
                </tbody>
            </table>
        );

        const error = <p style={{textAlign: "center"}}>{ this.state.error_text }</p>;

        return this.state.error ? error : table;
    }

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