import React, { Component } from "react";
const axios = require('axios');

class Functions extends Component {

    constructor(props){
        super(props);

        this.runAllUsers = this.runAllUsers.bind(this);
    }

    runAllUsers(event){
        axios.get('/api/playlist/run/users')
        .catch((error) => {
            console.log(error);
        });
    }

    render () {
        return ( 
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th>
                           <h1 className="text-no-select full-width center-text ui-text">admin functions</h1> 
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <button className="full-width button" onClick={this.runAllUsers}>run all users</button>
                        </td>
                    </tr>
                </tbody>
        </table>);
    }
}

export default Functions;