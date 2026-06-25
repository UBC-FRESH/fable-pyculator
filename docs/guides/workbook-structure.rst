FABLE-C Workbook Structure
==========================

Initial inspection used the public 2019, 2020, and 2021 open FABLE Calculator workbooks downloaded
into ignored local benchmark paths. The 2020 workbook is the primary benchmark for the first wrapper
because it is already the main Modelwright generated-model evidence target.

High-Level Structure
--------------------

The 2020 workbook contains 54 worksheets. The notebook interface should initially focus on three
surface areas:

- ``Indextables``: workbook metadata catalog for table names, roles, descriptions, and sources.
- ``SCENARIOS selection``: the main high-level scenario choice sheet.
- ``SCENARIOS definition``: detailed scenario parameter and formula tables used by the selected
  choices.

The core output data surfaces are a consecutive sequence of sheets:

``FOOD`` → ``PRODUCTION`` → ``TRADE`` → ``BIODIVERSITY`` → ``LAND`` → ``GHG`` → ``WATER``.

``SCENATHON_report`` appears immediately before this sequence and should be treated as a
report/summary surface rather than one of the core output-data sheets.

.. list-table::
   :header-rows: 1

   * - Sheet
     - Range
     - Excel tables
   * - ``FOOD``
     - ``A1:Z221``
     - ``Results_Diets``, ``Total_results_diets``
   * - ``PRODUCTION``
     - ``A1:X1002``
     - ``ResultsProd``, ``TotalResultsProd``
   * - ``TRADE``
     - ``A1:U1001``
     - ``ResultsTrade``, ``TotalResultsTrade``
   * - ``BIODIVERSITY``
     - ``A1:AD64``
     - ``ResultsBiodiv``, ``ResultsProtectedAreas``, ``ResultsTargetBiodiv``
   * - ``LAND``
     - ``A1:AI796``
     - ``ResultsLand``, ``ResultsCropArea``
   * - ``GHG``
     - ``A1:AJ47``
     - ``ResultsGHG``
   * - ``WATER``
     - ``A1:X1080``
     - ``TotalResultsWF``, ``ResultsWF``

The adjacent report sheet is:

.. list-table::
   :header-rows: 1

   * - Sheet
     - Range
     - Excel tables
   * - ``SCENATHON_report``
     - ``A1:BH1043``
     - ``Reporting_aggregate``, ``Reporting_byproduct``

Scenario Selection Controls
---------------------------

The 2020 and 2021 workbooks expose 16 high-level scenario controls on ``SCENARIOS selection``. Each
control is an Excel table. The first column is the selection marker; exactly one data row should
contain ``x``. The notebook control surface should display each table as a single dropdown and then
expand that choice into generated-model overrides that clear every marker cell except the selected
row.

.. list-table::
   :header-rows: 1

   * - Location
     - Table
     - Range
     - Options
     - 2020 default
   * - S.1
     - ``GDP_Scen``
     - ``A19:C22``
     - 3
     - ``SSP2``
   * - S.2
     - ``Pop_Scen``
     - ``A27:C41``
     - 14
     - ``SSP1``
   * - S.3
     - ``Diet_scen``
     - ``A46:D52``
     - 6
     - ``EATLancetAverage``
   * - S.4
     - ``Scen_foodloss``
     - ``A57:D60``
     - 3
     - ``Current``
   * - S.5
     - ``Scen_imports``
     - ``A65:D68``
     - 3
     - ``I2``
   * - S.6
     - ``Scen_exports``
     - ``A73:D76``
     - 3
     - ``E1``
   * - S.7
     - ``Live_scen``
     - ``A81:D85``
     - 4
     - ``BAUGrowth``
   * - S.8
     - ``Crop_scen``
     - ``A90:D94``
     - 4
     - ``HighGrowth``
   * - S.9
     - ``Land_Scen``
     - ``A99:D102``
     - 3
     - ``FreeExpansion``
   * - S.10
     - ``Affor_scen``
     - ``A107:D109``
     - 2
     - ``NoAffor``
   * - S.11
     - ``FixTrade_Scen``
     - ``A114:D116``
     - 2
     - ``No``
   * - S.12
     - ``PopActivity_Scen``
     - ``A121:D124``
     - 3
     - ``Middle``
   * - S.13
     - ``ClimateChange_Scen``
     - ``A129:D146``
     - 17
     - ``rcp6p0_hadgem2-es_n_GEPIC``
   * - S.14
     - ``PA_Scen``
     - ``A150:D152``
     - 2
     - ``NoChange``
   * - S.15
     - ``PostHarvestLoss_Scen``
     - ``A156:D158``
     - 2
     - ``Reduced``
   * - S.16
     - ``Biofuel_scen``
     - ``A162:D164``
     - 2
     - ``OECD_AGLINK``

Cross-Version Notes
-------------------

The 2020 and 2021 workbooks share the 16-control structure and nearly identical output-table
surfaces. The 2021 workbook differs in at least one default: ``Affor_scen`` defaults to
``BonnChallenge`` instead of the 2020 ``NoAffor`` default.

The 2019 workbook has only 12 discovered selection controls and fewer output sheets. It is useful as
a fragility and source-defect check, but it should not define the first control-surface contract.

``Indextables`` should drive user-guide labeling and output grouping. It records table names, roles
such as ``Scenario`` and ``Result Indicator``, table descriptions, and source/provenance text. It is
not an Excel Table object in the 2020 workbook, so the first parser should treat it as a structured
worksheet range with headers in row 1.

Package Mapping
---------------

``discover_selection_controls`` maps the S.1-S.16 tables into notebook dropdown declarations.
``discover_output_tables`` maps Excel tables on the seven canonical output data sheets into
DataFrame-ready table declarations.
