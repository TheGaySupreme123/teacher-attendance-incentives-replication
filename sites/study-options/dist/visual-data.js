window.researchVisualData = {
  "groups": [
    {
      "id": 0,
      "label": "Baseline nonwriters",
      "description": "Could not take the written baseline test",
      "arms": [
        {
          "label": "Control",
          "n": 858,
          "departed": 290,
          "rate": 33.7995337995338,
          "notDeparted": 568
        },
        {
          "label": "Program",
          "n": 940,
          "departed": 365,
          "rate": 38.82978723404255,
          "notDeparted": 575
        }
      ],
      "effect": 5.030253434508727,
      "low": -2.3640527805284175,
      "high": 12.424559649545872,
      "p": 0.1803733343097235
    },
    {
      "id": 1,
      "label": "Baseline writers",
      "description": "Took the written baseline test",
      "arms": [
        {
          "label": "Control",
          "n": 201,
          "departed": 89,
          "rate": 44.27860696517413,
          "notDeparted": 112
        },
        {
          "label": "Program",
          "n": 196,
          "departed": 138,
          "rate": 70.40816326530613,
          "notDeparted": 58
        }
      ],
      "effect": 26.129556300131945,
      "low": 9.99065246760524,
      "high": 42.268460132658646,
      "p": 0.0017480527079005727
    }
  ],
  "checks": [
    {
      "label": "Main analysis",
      "effect": 21.09930286562322,
      "low": 6.87285489338691,
      "high": 35.32575083785952,
      "p": 0.004011126002256849,
      "n": 2195
    },
    {
      "label": "Geographic controls",
      "effect": 22.10288190864485,
      "low": 8.244380913294236,
      "high": 35.961382903995464,
      "p": 0.002033416952736087,
      "n": 2195
    },
    {
      "label": "December 2005 endpoint",
      "effect": 19.69002145157843,
      "low": 4.800369405903587,
      "high": 34.579673497253275,
      "p": 0.01001615355390863,
      "n": 2195
    },
    {
      "label": "Exclude ambiguous departure codes",
      "effect": 26.62982921577478,
      "low": 12.02665180393855,
      "high": 41.23300662761101,
      "p": 0.0004564350637677392,
      "n": 2082
    }
  ],
  "quality": {
    "neither": 1965,
    "codeOnly": 85,
    "windowOnly": 117,
    "both": 28
  },
  "n": 2195,
  "originalMeanEffect": 8.368649692689573,
  "originalN": 2197,
  "sources": [
    "transition_scope_group_effects.csv",
    "transition_scope_model_results.csv",
    "sentinel_drop_interaction.csv",
    "measurement/sentinel_child_audit.csv"
  ]
};
