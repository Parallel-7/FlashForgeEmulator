"""
Printer mode definitions and feature management
"""
import config

class ModeFeatures:
    """Feature flags for different printer modes"""

    def __init__(self, mode):
        self.mode = mode
        self.has_camera = mode in [config.PrinterMode.PRO_5M, config.PrinterMode.AD5X]
        self.has_filtration = mode in [config.PrinterMode.PRO_5M, config.PrinterMode.AD5X]
        self.has_material_station = mode == config.PrinterMode.AD5X
        self.supports_multi_color = mode == config.PrinterMode.AD5X

    def get_product_control_states(self):
        """Get control states for /product endpoint based on mode"""
        return {
            "chamberTempCtrlState": 1 if self.has_filtration else 0,
            "externalFanCtrlState": 1 if self.has_filtration else 0,
            "internalFanCtrlState": 1 if self.has_filtration else 0,
            "lightCtrlState": 1,  # All modes have light control
            "nozzleTempCtrlState": 1,  # All modes have nozzle temp control
            "platformTempCtrlState": 1  # All modes have bed temp control
        }

class MaterialStationEmulator:
    """Emulate AD5X Material Station (IFS) functionality"""

    def __init__(self, config_slots=None):
        if config_slots:
            self.slots = config_slots.copy()
        else:
            self.slots = config.HTTP_CONFIG['material_station']['default_slots'].copy()

        self.current_slot = 1
        self.current_load_slot = 0
        self.state_action = 0
        self.state_step = 0

    def get_status(self):
        """Get current material station status for HTTP API"""
        return {
            "currentSlot": self.current_slot,
            "currentLoadSlot": self.current_load_slot,
            "slotCnt": len(self.slots),
            "slotInfos": self.slots,
            "stateAction": self.state_action,
            "stateStep": self.state_step
        }

    def update_slot(self, slot_id, has_filament=None, material_name=None, material_color=None):
        """Update material station slot"""
        for slot in self.slots:
            if slot['slotId'] == slot_id:
                if has_filament is not None:
                    slot['hasFilament'] = has_filament
                if material_name is not None:
                    slot['materialName'] = material_name
                if material_color is not None:
                    slot['materialColor'] = material_color
                break

    def set_current_slot(self, slot_id):
        """Set the currently active slot"""
        if 1 <= slot_id <= len(self.slots):
            self.current_slot = slot_id

    def set_loading_slot(self, slot_id):
        """Set the slot currently being loaded"""
        if 0 <= slot_id <= len(self.slots):
            self.current_load_slot = slot_id

def get_printer_name_for_mode(mode, base_name="FlashForge Adventurer"):
    """Get appropriate printer name for the mode"""
    mode_names = {
        config.PrinterMode.STANDARD_5M: f"{base_name} 5M",
        config.PrinterMode.PRO_5M: f"{base_name} 5M Pro",
        config.PrinterMode.AD5X: f"{base_name} 5X"
    }
    return mode_names.get(mode, base_name)

def get_machine_type_for_mode(mode):
    """Get machine type string for the mode"""
    mode_types = {
        config.PrinterMode.STANDARD_5M: "Adventurer 5M",
        config.PrinterMode.PRO_5M: "Adventurer 5M Pro",
        config.PrinterMode.AD5X: "Adventurer 5X"
    }
    return mode_types.get(mode, "Adventurer 5M")

def validate_material_mappings(material_mappings):
    """Validate AD5X material mappings"""
    if not isinstance(material_mappings, list):
        return False, "Material mappings must be a list"

    if len(material_mappings) == 0:
        return False, "Material mappings cannot be empty for multi-color jobs"

    if len(material_mappings) > 4:
        return False, "Maximum 4 material mappings allowed"

    import re
    hex_color_regex = re.compile(r'^#[0-9A-Fa-f]{6}$')

    for i, mapping in enumerate(material_mappings):
        # Check required fields
        required_fields = ['toolId', 'slotId', 'materialName', 'toolMaterialColor', 'slotMaterialColor']
        for field in required_fields:
            if field not in mapping:
                return False, f"Missing required field '{field}' in mapping {i}"

        # Validate toolId (0-3)
        if not isinstance(mapping['toolId'], int) or not (0 <= mapping['toolId'] <= 3):
            return False, f"toolId must be between 0-3, got {mapping['toolId']} at index {i}"

        # Validate slotId (1-4)
        if not isinstance(mapping['slotId'], int) or not (1 <= mapping['slotId'] <= 4):
            return False, f"slotId must be between 1-4, got {mapping['slotId']} at index {i}"

        # Validate materialName is not empty
        if not mapping['materialName'] or mapping['materialName'].strip() == '':
            return False, f"materialName cannot be empty at index {i}"

        # Validate color formats
        if not hex_color_regex.match(mapping['toolMaterialColor']):
            return False, f"toolMaterialColor must be in #RRGGBB format, got {mapping['toolMaterialColor']} at index {i}"

        if not hex_color_regex.match(mapping['slotMaterialColor']):
            return False, f"slotMaterialColor must be in #RRGGBB format, got {mapping['slotMaterialColor']} at index {i}"

    return True, "Valid"