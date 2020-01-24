import React, { Component } from "react";
import { BrowserRouter as Router, Route, Link, Switch, Redirect} from "react-router-dom";
const axios = require('axios');

import Edit from "./Edit.js";
import Count from "./Count.js";

class View extends Component{

    render() {
        return (
            <table className="app-table max-width">
                <thead>
                    <tr>
                        <th colSpan="2"><h1 className="text-no-select">{ this.props.match.params.name }</h1></th>
                    </tr>
                    <tr>
                        <th colSpan="2">
                            <div>
                                <ul className="navbar" style={{width: "100%"}}>
                                    <li><Link to={`${this.props.match.url}/edit`}>Edit</Link></li>
                                    <li><Link to={`${this.props.match.url}/count`}>Count</Link></li>
                                </ul>
                            </div>
                        </th>
                    </tr>
                </thead>
                <Route path={`${this.props.match.url}/edit`} render={(props) => <Edit {...props} name={this.props.match.params.name}/>} />
                <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />
            </table>
        );
    }

}

export default View;