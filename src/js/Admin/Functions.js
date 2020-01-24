import React, { Component } from "react";
const axios = require('axios');

import showMessage from "../Toast.js"

class Functions extends Component {

    constructor(props){
        super(props);

        this.runAllUsers = this.runAllUsers.bind(this);
        this.runStats = this.runStats.bind(this);
    }

    runAllUsers(event){
        axios.get('/api/playlist/run/users')
        .then((response) => {
            showMessage('Users Run');
        })
        .catch((error) => {
            showMessage(`Error Running All Users (${error.response.status})`);
        });
    }

    runStats(event){
        axios.get('/api/spotfm/playlist/refresh/users')
        .then((response) => {
            showMessage('Stats Run');
        })
        .catch((error) => {
            showMessage(`Error Running All Users (${error.response.status})`);
        });
    }

    render () {
        return ( 
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th>
                           <h1 className="text-no-select full-width center-text ui-text">Admin Functions</h1> 
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <button className="full-width button" onClick={this.runAllUsers}>Run All Users</button>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <button className="full-width button" onClick={this.runStats}>Run Stats</button>
                        </td>
                    </tr>
                </tbody>
        </table>);
    }
}

export default Functions;