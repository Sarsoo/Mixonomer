import React, { Component } from "react";
import { Route, Link, Switch } from "react-router-dom";
import { ThemeProvider } from '@material-ui/core/styles';

import { Paper, Tabs, Tab } from '@material-ui/core';

import GlobalTheme from "../../Theme.js" 

import {Edit} from "./Edit.js";
import {Count} from "./Count.js";

class View extends Component{

    constructor(props){
        super(props);
        this.state = {
            tab: 0
        }
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e, newValue){
        this.setState({
            tab: newValue
        });
    }

    render() {
        return (
            <div>
            <ThemeProvider theme={GlobalTheme}>
                <Paper>
                    <Tabs
                        value={this.state.tab}
                        onChange={this.handleChange}
                        indicatorColor="primary"
                        textColor="secondary"
                        centered
                    >
                        <Tab label="Edit" component={Link} to={`${this.props.match.url}/edit`} />
                        <Tab label="Count" component={Link} to={`${this.props.match.url}/count`} />
                    </Tabs>
                </Paper>
            </ThemeProvider>
            <Switch>
                <Route path={`${this.props.match.url}/edit`} render={(props) => <Edit {...props} name={this.props.match.params.name}/>} />
                <Route path={`${this.props.match.url}/count`} render={(props) => <Count {...props} name={this.props.match.params.name}/>} />
            </Switch>
            </div>
        );
    }

}

export default View;