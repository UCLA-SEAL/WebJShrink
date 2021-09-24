import React, { Component } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { HorizontalBar, Pie, Bar } from 'react-chartjs-2';
import { Line } from 'rc-progress';
import logo from './logo.svg';
import './App.css';
import './Landing.css';
import {LoaderWithMessage} from './components/LoaderWithMessage';
import mradawa from './mradawa.png';
import webjshrink from './webJshrink.png';
import * as plot from './plottingUtils';
import {SERVER_URL, ANALYSIS_ROUTE, DEBLOAT_ROUTE, DOWNLOAD_ROUTE, GITHUB_REPO_URL} from './routes';
import * as TXT from './plaintext';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      api_data: {},
      pie_data_classes: {},
      pie_data_methods: {},
      plot_data: {},
      display_classes: [],
      api_list: [],
      message: '',
      hasError: false,
      library_to_classes: {},
      libraries: [],
      debloat_request_status: '',
      debloat_info: {},
      reponame: '',
      methods: [
        { value: 'test', label: 'Test' },
        { value: 'main', label: 'Main' }
      ],
      selected_methods: [
      ]
    };
  };

  getCallGraphAnalysisOptions = () => {
    return {
      mainEntry: +this.refs.mainEntry.checked,
      publicEntry: +this.refs.publicEntry.checked,
      testEntry: +this.refs.testEntry.checked,
      spark: +this.refs.spark.checked,
      cha: +this.refs.cha.checked,
      tamiflex: +this.refs.tamiflex.checked,
      jmtrace: +this.refs.jmtrace.checked
    }
  }

  getDebloatOptions = () => {
    return {
      pruneApp: +this.refs.pruneApp.checked,
      checkpointing: +this.refs.checkpointing.checked,
      removeMethods: +this.refs.removeMethods.checked,
      removeOnlyMethodBody: +this.refs.removeOnlyMethodBody.checked,
      removeMethodBodyWithMessage: +this.refs.removeMethodBodyWithMessage.checked,
      removeBodyMessage: this.refs.removeBodyMessage.value || "Debloated by Mradawa"
    }
  }

  requestAnalysisSetData = () => {
    const userRef = this.refs.user;
    const repoRef = this.refs.repo;
    var _this = this;
    let reponame = repoRef.value || 'curator';
    let username = userRef.value;
    let url = SERVER_URL;
    let github_url = GITHUB_REPO_URL;
    if (username && reponame) {
      url = url + 'github/' + username + '/' + reponame
      github_url = github_url + username + '/' + reponame
    } else {
      url = url + 'repo/' + reponame
    }

    url = SERVER_URL + ANALYSIS_ROUTE + username + '/' + reponame;
    const FORM_SUBMISSION_MSG = `Analyzing ${username}/${reponame}. ${TXT.WILL_TAKE_TIME}`;

    axios.get(github_url).then(response => {
      axios.get(url, {
        origin: 'http://localhost:3000',
        withCredentials: true,
        params: this.getCallGraphAnalysisOptions()
      }).then(response => {
          if (response.data.error) {
            this.setState({
              message: response.data.error,
              hasError: true,
              plot_data: {},
              pie_data: {}
            })
          } else {
            const api_data = response.data;
            const { lib_names, used_counts, total_counts, library_classes_obj, library_methods } 
            = plot.processLibraryDataForCharts(api_data.libraries);

            this.setState({
              pie_data_classes: plot.getClassesPieChart(api_data),
              pie_data_methods: plot.getMethodsPieChart(api_data),
              plot_data: plot.getUsedUnusedPlotData(lib_names, total_counts, used_counts),
              api_data: api_data,
              message: 'Here are the results for ' + reponame,
              library_to_classes: library_classes_obj,
              reponame: reponame,
              methods: library_methods
            });
          }})
    }).catch((err) => {
      this.setState({
        message: TXT.INVALID_REPO,
        hasError: true,
        plot_data: {},
        pie_data: {}
      });
    });

    this.setState({
      message: FORM_SUBMISSION_MSG,
      plot_data: {},
      pie_data: {}
    });
  }

  getGraphElementInfo = (e) => {
    if (!e[0] || !e[0]._model) return;
    let class_name = e[0]._model.label;
    let classes = this.state.library_to_classes[class_name].classes;
    this.setState({
      display_classes: classes
    })
  }

  handleMethodsSelected = (selectedOptions) => {
    this.setState({
      selected_methods: selectedOptions
    })
    console.log(`Option selected:`, selectedOptions);
  }

  refresh = () => {
    window.location.reload(false);
  }

  requestDebloat = () => {
    let _this = this;
    let url = SERVER_URL + DEBLOAT_ROUTE + this.state.reponame;
    let selected_methods = this.state.selected_methods;
    let selectedMethods = selected_methods.map(function (m) {
      return m.value
    })
    axios.get(url, {
      withCredentials: true,
      params: this.getDebloatOptions()
    }).then(function (response) {
      _this.setState({
        debloat_info: response.data,
        debloat_request_status: 'data-received'
      })
    })
      .catch(function (error) {
        console.log(error);
      });

    this.setState({
      debloat_request_status: 'sent'
    })
  }

  dismissClassesDisplay = (e) => {
    this.setState({
      display_classes: []
    })
  }

  getVisualizations() {
    let display_classes = this.state.display_classes;
    let classes_container = '';
    if (display_classes.length != 0) {
      classes_container =
        <div className="used-classes box-shadow">
          <div className="popup-header">
            <button className="dismiss" onClick={this.dismissClassesDisplay}>Dismiss</button>
          </div>
          Classes in Library
          {
            display_classes.map(function (cl, i) {
              let color = '#71B37C'; // green meaning used
              if (cl.used_methods_count === 0) {
                color = '#ff6384';
              }
              return <p className="used-class" style={{ color: color }} key={i} >{cl.class_name}</p>
            })
          }
        </div>
    }

    return (
      <div>
        <div className='results-container'>
          <div className='libraries-container'>
            <h4>Used and Unused Classes</h4>
            <Pie data={this.state.pie_data_classes} />
            <br />
            <h4>Used and Unused Methods</h4>
            <Pie data={this.state.pie_data_methods} />
          </div>
          <div className='graph-container'>
            <h4>Used and Unused Classes by Library</h4>
            <HorizontalBar data={this.state.plot_data} onElementsClick={this.getGraphElementInfo} 
              options={plot.barChartOptions}
            />
          </div>
        </div>
        {classes_container}
      </div>
    )
  }

  getLandingForm() {
    return (
      <div className='form-container'>
        <img className='webjshrink-logo' src={webjshrink} />    
        {/*<h2 className='page-title'>Maven Repository Analysis & Debloating Web Application</h2>*/}
        <p>Enter a Github Repository for a maven project for analyzing software bloat</p>
        <div className='input-container'>
          <input className='input' ref="user" placeholder="Github Username"></input>
          <input className='input' ref="repo" placeholder="Repository"></input>
          <a onClick={this.requestAnalysisSetData} className='post-submit-button' href="#">
            Submit
        </a>
        </div>
        <div className='options-container box-shadow'>
          <p className='option-header'>Select an Entrypoint:</p>
          <div className='analysis-options-container'>
            <div className='checkbox-container'>
              <input className='checkbox' type="checkbox" ref="mainEntry" defaultChecked="1" /> Use Main Entry
          </div>
            <div className='checkbox-container'>
              <input className='checkbox' type="checkbox" ref="publicEntry" /> Use Public Entry
          </div>
            <div className='checkbox-container'>
              <input className='checkbox' type="checkbox" ref="testEntry" /> Use Test Entry
          </div>
          </div>
          <p className='option-header'>Select Call Graph Analysis options</p>
          <div className='analysis-options-container'>
            <div className='checkbox-container'>
              <input className='checkbox' type="checkbox" ref="tamiflex" /> Use Tamiflex
          </div>
            <div className='checkbox-container'>
              <input className='checkbox' type="checkbox" ref="jmtrace" /> Use JMTrace
          </div>
            <div className='checkbox-container'>
              <input className='checkbox' type="radio" name="spark-or-cha" ref="spark" /> Use Spark
          </div>
            <div className='checkbox-container'>
              <input className='checkbox' type="radio" name="spark-or-cha" ref="cha" defaultChecked="1" /> Use CHA
          </div>
          </div>
        </div>
      </div>
    )
  }

  getDebloatSection() {
    let debloat_section = '';
    let _this = this;
    if (this.state.debloat_request_status == '') {
      debloat_section =
        <div>
          <h4>You can debloat and download the minified repository.</h4>
          <div className='debloat-section box-shadow'>
            <span className='option-header'>Choose options for debloating.</span>
            <div className='options-container'>
              <div className='checkbox-container'>
                <input className='checkbox' type="checkbox" ref="pruneApp" /> Prune App
              </div>
              <div className='checkbox-container'>
                <input className='checkbox' type="checkbox" ref="checkpointing" /> Use Checkpointing for Complete Behaviour Preservation
              </div>
              <div className='checkbox-container'>
                <input className='checkbox' type="radio" name="removeMethodRadio" ref="removeMethods" defaultChecked="1" /> Remove Entire Method
              </div>
              <div className='checkbox-container'>
                <input className='checkbox' type="radio" name="removeMethodRadio" ref="removeOnlyMethodBody" /> Remove Only Method Body (preserves definition)
              </div>
              <div className='checkbox-container'>
                <input className='checkbox' type="radio" name="removeMethodRadio" ref="removeMethodBodyWithMessage" /> Replace Method Body with Message:
                <input className='input-message' ref="removeBodyMessage" placeholder="Debloated by WebJshrink"></input>
              </div>
            </div>
            <a onClick={this.requestDebloat} className='post-submit-button'>
              Debloat this Repository
          </a>
            <a onClick={this.refresh} className='post-submit-button'>
              Run Analysis on another Repository
          </a>
          </div>
        </div>
    }
    if (this.state.debloat_request_status == 'sent') {
      debloat_section = LoaderWithMessage(`${TXT.DEBLOAT_SUBMIT_MESSAGE} ${TXT.WILL_TAKE_TIME}`);
    }
    if (this.state.debloat_request_status == 'data-received') {
      let info = _this.state.debloat_info;
      let download_link = SERVER_URL + DOWNLOAD_ROUTE + this.state.reponame;
      let testPassedPercent = ((info['total_number_tests'] - info['total_tests_failed'])/info['total_number_tests'])*100;
      let strokeColor = testPassedPercent > 70 ? '#71B37C' : '#e88733';
      let testPreservationStr = 
      `
      ${testPassedPercent}% of tests pass in the debloated repo! (${info['total_tests_failed']} out of ${info['total_number_tests']} tests failed)
      `;
      debloat_section =
        <div className='debloat-info-container box-shadow'>
          <center>
            <p><b>Debloat Statistics</b></p>
             {plot.getDebloatStatisticsTable(info)}
          </center>
            <div className='debloat-other-info'>
              {testPreservationStr}
              <Line percent={testPassedPercent} strokeWidth="4" strokeColor={strokeColor} />
              <p><b>Time Elapsed:</b> {info["time_elapsed"]} seconds</p>
            </div>
          <a href={download_link} className="post-submit-button" download>{TXT.DOWNLOAD_DEBLOATED_REPO}</a>
          <a onClick={this.refresh} className='post-submit-button'>
            {TXT.RUN_ANOTHER_ANALYSIS}
          </a>
        </div>
    }
    return (
      debloat_section
    )
  }

  render() {
    let github_form = this.getLandingForm();
    let results = '';
    let loader = '';
    let debloat_section = '';

    if (Object.keys(this.state.plot_data).length !== 0) {
      github_form = '';
      results = this.getVisualizations();
      debloat_section = this.getDebloatSection();
    }

    if (Object.keys(this.state.plot_data).length === 0
      && (this.state.message != '' && !this.state.hasError)) {
      loader =
        <div>
          <div className='spinner'></div>
          {TXT.ANALYSES_SUBMIT_MESSAGE}
        </div>
    }

    return (
      <div className="App">
        <div className={'landing-container'}>
          {github_form}
          <h4>{this.state.message}</h4>
          {loader}
          {results}
          {debloat_section}
        </div>
      </div>
    );
  }
}

export default App;