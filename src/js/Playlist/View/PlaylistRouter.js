import React, { Component } from "react";
import { Route, Link, Switch } from "react-router-dom";
import { Paper, Tabs, Tab} from '@material-ui/core';


import {Edit} from "./Edit.js";
import {Count} from "./Count.js";

/**
 * Playlist view structure with tabs for view/editing and statistics
 */
class View extends Component{

    constructor(props){
        super(props);
        this.state = {
            tab: 0
        }
        this.handleChange = this.handleChange.bind(this);
    }

    /**
     * Handle tab change event
     * @param {*} e Event args
     * @param {*} newValue New tab object
     */
    handleChange(e, newValue){
        this.setState({
            tab: newValue
        });
    }

    render() {
        return (
            <div>
            <Paper>
                <Tabs
                    value={this.state.tab}
                    onChange={this.handleChange}
                    indicatorColor="primary"
                    centered
                    width="50%"
                >

                    {/* VIEW/EDIT */}
                    <Tab label="Edit" component={Link} to={`${this.props.match.url}/edit`} />

                    {/* STATS */}
                    <Tab label="Count" component={Link} to={`${this.props.match.url}/count`} />
                </Tabs>
            </Paper>
            <Switch>

                {/* VIEW/EDIT */}
                <Route path={`${this.props.match.url}/edit`} render={(props) => <Edit {...props} name={this.props.match.params.name}/>} />
                
                {/* STATS */}
                <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />
            </Switch>
            </div>
        );
    }

}

export default View;